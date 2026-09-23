import { SafeAreaView } from "react-native-safe-area-context";
import {
  Text,
  Image,
  ActivityIndicator,
  View,
  TouchableOpacity,
} from "react-native";
import { usePlatformSettings } from "@/contexts/PlatformSettingsContext";

export default function Login() {
  const { platformSettings, isLoading } = usePlatformSettings();

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-200">
      {/* 1. FIXED TOP LOGO ZONE */}
      <View className="items-center mt-14">
        {platformSettings?.siteLogo && (
          <Image
            source={{ uri: platformSettings.siteLogo }}
            className="w-64 h-64 relative right-2"
            resizeMode="contain"
          />
        )}
      </View>

      {/* 2. DYNAMIC MIDDLE ZONE (Takes remaining space) */}
      <View className="flex-1 items-center justify-top px-6 pt-2">
        <Text className="text-center text-4xl font-bold">Welcome to AFI</Text>
        <Text className="text-center mt-2 text-lg font-bold w-4/5">
          Everything you need to know about your freshman journey in one place.
        </Text>
      </View>

      {/* 3. FIXED BOTTOM CTA ZONE */}
      <View className="w-full px-6 pb-24 items-center">
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={() => {
            // Navigation logic
          }}
          className="w-full bg-[#1d4f8f] py-4 rounded-2xl items-center justify-center"
        >
          <Text className="text-white text-lg font-bold tracking-wide">
            Get Started
          </Text>
        </TouchableOpacity>

        <Text className="text-gray-600 font-medium text-sm mt-4 text-center">
          Built for AASTU freshmen
        </Text>
      </View>
    </SafeAreaView>
  );
}
