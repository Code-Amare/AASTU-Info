import { Stack, useRouter, useSegments } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { PlatformSettingsProvider } from "@/contexts/PlatformSettingsContext";
function AppNavigator() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(public)" />
    </Stack>
  );
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
