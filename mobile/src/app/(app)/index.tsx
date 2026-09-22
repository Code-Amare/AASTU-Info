import { Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useAuth } from "@/contexts/AuthContext";

export default function AppHome() {
  const { user } = useAuth();

  return (
    <SafeAreaView className="flex-1">
      <View className="flex-1 items-center justify-center">
        <Text className="text-2xl font-semibold">
          Hello, {user?.full_name || user?.first_name || user?.username}
        </Text>
      </View>
    </SafeAreaView>
  );
}
