import React, {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api, { clearTokens, getAccessToken, setTokens } from "@/services/api";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

export interface User {
  id: string;
  username: string;
  email: string;

  first_name: string;
  last_name: string;
  full_name: string;

  role: "student" | "teacher" | "admin";

  phone_number: string;
  date_of_birth: string | null;
  profile_picture: string | null;

  department: number | null;
  section: string;

  email_verified: boolean;
  two_factor_enabled: boolean;

  is_staff: boolean;
  is_superuser: boolean;
}

interface LoginSuccessResponse {
  access: string;
  refresh: string;
  user: User;
}

interface TwoFactorRequiredResponse {
  detail: string;
  twofa_required: true;
}

interface VerificationRequiredResponse {
  error: string;
  verification_required: true;
  email: string;
}

export type LoginResult =
  | { status: "success"; user: User }
  | {
      status: "two_factor_required";
      message: string;
    }
  | {
      status: "verification_required";
      email: string;
      message: string;
    };

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (usernameOrEmail: string, password: string) => Promise<LoginResult>;

  logout: () => Promise<void>;

  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async (): Promise<void> => {
    const response = await api.get<User>("/api/users/me/");

    setUser(response.data);
  }, []);

  useEffect(() => {
    let mounted = true;

    async function initializeAuth(): Promise<void> {
      try {
        const accessToken = await getAccessToken();

        if (!accessToken) {
          return;
        }

        const response = await api.get<User>("/api/users/me/");

        if (mounted) {
          setUser(response.data);
        }
      } catch {
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    void initializeAuth();

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(
    async (usernameOrEmail: string, password: string): Promise<LoginResult> => {
      const response = await api.post<
        | LoginSuccessResponse
        | TwoFactorRequiredResponse
        | VerificationRequiredResponse
      >("/api/users/login/", {
        username_or_email: usernameOrEmail.trim(),
        password,
      });

      const data = response.data;

      // Email verification is required.
      if ("verification_required" in data) {
        return {
          status: "verification_required",
          email: data.email,
          message: data.error,
        };
      }

      // Two-factor login link was sent.
      if ("twofa_required" in data) {
        return {
          status: "two_factor_required",
          message: data.detail,
        };
      }

      // Validate the successful login response.
      if (!("access" in data) || !("refresh" in data) || !("user" in data)) {
        throw new Error("Unexpected login response from the server.");
      }

      await setTokens(data.access, data.refresh);

      setUser(data.user);

      return {
        status: "success",
        user: data.user,
      };
    },
    [],
  );

  const logout = useCallback(async (): Promise<void> => {
    try {
    } finally {
      await clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider.");
  }

  return context;
}
