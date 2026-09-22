import React, {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api, {
  clearTokens,
  getAccessToken,
  setTokens,
} from "@/services/api";

export interface User {
  id: string;
  username: string;
  email: string;

  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;

  phone_number: string | null;
  date_of_birth: string | null;
  profile_picture: string | null;

  email_verified: boolean;
  two_factor_enabled: boolean;

  is_owner: boolean;
  is_staff: boolean;
  is_superuser: boolean;
}

interface LoginResponse {
  access: string;
  refresh: string;
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => Promise<void>;

  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export function AuthProvider({
  children,
}: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Fetch the currently authenticated user.
   */
  const refreshUser = useCallback(async () => {
    const response = await api.get<User>("/api/users/me/");

    setUser(response.data);
  }, []);

  /**
   * Restore the authentication state when the app starts.
   */
  useEffect(() => {
    let mounted = true;

    async function initializeAuth() {
      try {
        const accessToken = await getAccessToken();

        if (!accessToken) {
          return;
        }

        const response = await api.get<User>(
          "/api/users/me/"
        );

        if (mounted) {
          setUser(response.data);
        }
      } catch {
        /*
         * api.ts handles access-token refresh automatically.
         *
         * If the refresh token is also invalid/expired,
         * the API layer clears the stored tokens.
         */
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    initializeAuth();

    return () => {
      mounted = false;
    };
  }, []);

  /**
   * Authenticate the user.
   */
  const login = useCallback(
    async (email: string, password: string) => {
      const response = await api.post<LoginResponse>(
        "/api/users/login/",
        {
          email,
          password,
        }
      );

      const { access, refresh } = response.data;

      await setTokens(access, refresh);

      /*
       * Get the authoritative user data from Django
       * after authentication.
       */
      const userResponse = await api.get<User>(
        "/api/users/me/"
      );

      setUser(userResponse.data);
    },
    []
  );

  /**
   * Log the user out locally.
   */
  const logout = useCallback(async () => {
    try {
      /*
       * If Django later gets a refresh-token blacklist
       * endpoint, call it here before clearing local tokens.
       */
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
    [
      user,
      isLoading,
      login,
      logout,
      refreshUser,
    ]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Access authentication state from any component.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider."
    );
  }

  return context;
}