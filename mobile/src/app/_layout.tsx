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
  const isInsideAuth = segments[0] === "(auth)";

  // Routes accessible without authentication
  const isUnprotectedRoute = isInsidePublic || isInsideAuth;

  useEffect(() => {
    if (isLoading) return;

    // User is NOT logged in and trying to access a protected screen
    if (!user && !isUnprotectedRoute) {
      router.replace("/(auth)");
    }
    // User IS logged in and inside (public) screen (optional redirect to app home)
    else if (user && isInsidePublic) {
      router.replace("/");
    }
  }, [user, isLoading, segments]);

  // Prevent rendering <Stack /> until loading is done and auth redirect check passes
  if (isLoading || (!user && !isUnprotectedRoute)) {
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
