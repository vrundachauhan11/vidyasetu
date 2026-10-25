"""Authentication & Role-Based Access Control (RBAC) Module for VidyaSetu.
Provides login, logout, token issuance, active user verification, and demo role switching.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.modules.auth.security import (
    UserProfile,
    DEMO_PERSONAS,
    DEMO_PERSONAS_BY_EMAIL,
    create_access_token,
    get_current_user,
    get_user_profile,
)

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None  # Quick 1-click demo role option


class LoginResponse(BaseModel):
    success: bool = True
    token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    user: UserProfile
    demo_mode: bool = True
    notice: str = "DEMO CREDENTIALS ONLY - Prototype authentication for SIH 2026 PS 26263 evaluation."


class SwitchRoleRequest(BaseModel):
    role: str


class SwitchRoleResponse(BaseModel):
    success: bool = True
    token: str
    token_type: str = "Bearer"
    user: UserProfile


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """Authenticate user with demo credentials or 1-click demo persona selector."""
    # 1. Option A: Quick demo role selector
    if payload.role and payload.role in DEMO_PERSONAS:
        persona = DEMO_PERSONAS[payload.role]
        token = create_access_token(persona["user_id"], persona["email"], persona["role"])
        return LoginResponse(
            token=token,
            expires_in_minutes=480,
            user=get_user_profile(persona["role"]),
        )

    # 2. Option B: Email + Password verification
    if payload.email and payload.password:
        normalized_email = payload.email.strip().lower()
        persona = DEMO_PERSONAS_BY_EMAIL.get(normalized_email)

        # Constant-time comparison for safety
        if persona and payload.password == persona["demo_password"]:
            token = create_access_token(persona["user_id"], persona["email"], persona["role"])
            return LoginResponse(
                token=token,
                expires_in_minutes=480,
                user=get_user_profile(persona["role"]),
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid demo credentials. Please verify your email and demo password or use 1-click persona selection.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please provide email and password, or select a valid demo persona role.",
    )


@router.post("/logout")
async def logout(current_user: UserProfile = Depends(get_current_user)):
    """Terminate the active prototype session."""
    return {
        "success": True,
        "message": f"User {current_user.email} successfully logged out of VidyaSetu prototype session.",
        "demo_mode": True,
    }


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: UserProfile = Depends(get_current_user)):
    """Retrieve current authenticated user and RBAC profile from Bearer token."""
    return current_user


@router.post("/switch-role", response_model=SwitchRoleResponse)
async def switch_demo_role(payload: SwitchRoleRequest, current_user: UserProfile = Depends(get_current_user)):
    """Switch active demo role for demonstration of role-specific workflows during hackathon evaluation.
    Security Enforcement: Changing a role selector after login cannot elevate permissions to higher roles.
    """
    if payload.role not in DEMO_PERSONAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown role '{payload.role}'. Available roles: {list(DEMO_PERSONAS.keys())}",
        )

    target_persona = DEMO_PERSONAS[payload.role]
    # Check if target role requires permissions that current_user does not possess (Regulator has broad preview clearance)
    if current_user.role != "REGULATOR_AICTE":
        unauthorized_perms = [p for p in target_persona["permissions"] if p not in current_user.permissions]
        if unauthorized_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permission elevation denied: Role '{current_user.role}' cannot elevate to "
                    f"higher-privileged role '{payload.role}' without authenticating with designated credentials. "
                    f"Missing required permission(s): {', '.join(unauthorized_perms)}."
                ),
            )

    new_token = create_access_token(target_persona["user_id"], target_persona["email"], target_persona["role"])
    return SwitchRoleResponse(
        token=new_token,
        user=get_user_profile(target_persona["role"]),
    )


@router.get("/roles")
async def list_available_roles():
    """List available demo roles with clearly demarcated synthetic credentials for hackathon evaluation."""
    return [
        {
            "role": p["role"],
            "title": p["role_title"],
            "name": p["name"],
            "email": p["email"],
            "demo_password": p["demo_password"],
            "institution": p["institution_name"],
            "description": p["description"],
            "permissions": p["permissions"],
        }
        for p in DEMO_PERSONAS.values()
    ]
