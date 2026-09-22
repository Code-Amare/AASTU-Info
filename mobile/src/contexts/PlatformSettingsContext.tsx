import React, {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "@/services/api";

export interface PlatformSettings {
  siteName: string;
  siteLogo: string;
  supportEmail: string;
  supportPhoneNumber: number;
}

interface PlatformSettingsContextValue {
  platformSettings: PlatformSettings | null;
  isLoading: boolean;
}

const PlatformSettingsContext =
  createContext<PlatformSettingsContextValue | undefined>(undefined);

export function PlatformSettingsProvider({
  children,
}: PropsWithChildren) {
  const [platformSettings, setPlatformSettings] =
    useState<PlatformSettings | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const getSettings = async () => {
      try {
        const response = await api.get<PlatformSettings>(
          "/api/console/settings/"
        );

        if (mounted) {
          setPlatformSettings(response.data);
        }
      } catch {
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
    [platformSettings, isLoading]
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
      "usePlatformSettings must be used within a PlatformSettingsProvider"
    );
  }

  return context;
}