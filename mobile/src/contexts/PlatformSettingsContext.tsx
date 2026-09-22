import React, {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "@/services/api";

// 1. Raw structure returned by the backend
interface ApiPlatformSettings {
  site_name: string;
  site_logo: string;
  support_email: string;
  support_phone: string;
  updated_at: string;
}

// 2. Mapped structure used in your React application
export interface PlatformSettings {
  siteName: string;
  siteLogo: string;
  supportEmail: string;
  supportPhoneNumber: string; // Keep as string to avoid dropping leading zeros (e.g., "0980495484")
}

interface PlatformSettingsContextValue {
  platformSettings: PlatformSettings | null;
  isLoading: boolean;
}

const PlatformSettingsContext = createContext<
  PlatformSettingsContextValue | undefined
>(undefined);

export function PlatformSettingsProvider({ children }: PropsWithChildren) {
  const [platformSettings, setPlatformSettings] =
    useState<PlatformSettings | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const getSettings = async () => {
      try {
        const response = await api.get<ApiPlatformSettings>(
          "/api/console/settings/",
        );

        if (mounted) {
          const raw = response.data;
          // Map backend snake_case keys to frontend camelCase properties
          setPlatformSettings({
            siteName: raw.site_name,
            siteLogo: raw.site_logo,
            supportEmail: raw.support_email,
            supportPhoneNumber: raw.support_phone,
          });
        }
      } catch (err) {
        console.error(err);
        if (mounted) {
          setPlatformSettings(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    getSettings();

    return () => {
      mounted = false;
    };
  }, []);

  const value = useMemo<PlatformSettingsContextValue>(
    () => ({
      platformSettings,
      isLoading,
    }),
    [platformSettings, isLoading],
  );

  return (
    <PlatformSettingsContext.Provider value={value}>
      {children}
    </PlatformSettingsContext.Provider>
  );
}

export function usePlatformSettings() {
  const context = useContext(PlatformSettingsContext);

  if (!context) {
    throw new Error(
      "usePlatformSettings must be used within a PlatformSettingsProvider",
    );
  }

  return context;
}
