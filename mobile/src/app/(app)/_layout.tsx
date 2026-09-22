import { Redirect, Stack } from "expo-router";
import { ActivityIndicator, View } from "react-native";
import { useAuth } from "@/contexts/AuthContext";

export default function AppLayout() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator size="large" />
      </View>
    );
  }

  // If user is not logged in, redirect to (public)
  if (!user) {
    return <Redirect href="/(public)" />;
  }

  return <Stack screenOptions={{ headerShown: false }} />;
}
