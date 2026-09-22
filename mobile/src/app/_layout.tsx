import { Stack, useRouter, useSegments } from "expo-router";
import { useEffect } from "react";
import { ActivityIndicator, View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { PlatformSettingsProvider } from "@/contexts/PlatformSettingsContext";

function AppNavigator() {
  const { user, isLoading } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  const isInsidePublic = segments[0] === "(public)";

  useEffect(() => {
    if (isLoading) return;

    // User is NOT logged in and trying to access protected screen
    if (!user && !isInsidePublic) {
      router.replace("/(public)");
    }
    // User IS logged in and trying to access public/login screen
    else if (user && isInsidePublic) {
      router.replace("/");
    }
  }, [user, isLoading, segments]);

  // Prevent rendering <Stack /> until loading is done and auth redirect decision is complete
  if (isLoading || (!user && !isInsidePublic)) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return <Stack screenOptions={{ headerShown: false }} />;
}

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <PlatformSettingsProvider>
          <AppNavigator />
        </PlatformSettingsProvider>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
