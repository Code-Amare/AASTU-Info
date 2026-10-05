import { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import {
  Text,
  Image,
  ActivityIndicator,
  View,
  TouchableOpacity,
  TextInput,
} from "react-native";
import { Eye, EyeOff } from "lucide-react-native";

import { usePlatformSettings } from "@/contexts/PlatformSettingsContext";
import { useAuth } from "@/contexts/AuthContext";

export default function Login() {
  const { platformSettings, isLoading: settingsLoading } =
    usePlatformSettings();

  const { login } = useAuth();
  const router = useRouter();

  const [usernameOrEmail, setUsernameOrEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isPasswordVisible, setIsPasswordVisible] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (): Promise<void> => {
    setError(null);

    if (!usernameOrEmail.trim() || !password) {
      setError("Please enter your username/email and password.");
      return;
    }

    try {
      setIsSubmitting(true);

      const result = await login(usernameOrEmail, password);

      if (result.status === "success") {
        // Your Expo Router authentication layout can redirect
        // when the authenticated state changes.
        router.replace("/");
        return;
      }

      if (result.status === "two_factor_required") {
        setError(result.message);
        // Add navigation to your two-factor verification screen here.
        return;
      }

      if (result.status === "verification_required") {
        // Add navigation to your email verification screen here.
        router.push({
          //   pathname: "/(auth)/verify-email",
          pathname: "/",
          params: { email: result.email },
        });
      }
    } catch (error: unknown) {
      const message =
        typeof error === "object" && error !== null && "response" in error
          ? ((
              error as {
                response?: {
                  data?: {
                    error?: string;
                    detail?: string;
                  };
                };
              }
            ).response?.data?.error ??
            (
              error as {
                response?: {
                  data?: {
                    detail?: string;
                  };
                };
              }
            ).response?.data?.detail)
          : null;

      setError(message ?? "Unable to sign in. Please check your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (settingsLoading) {
    return (
      <SafeAreaView className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 items-center">
      {/* 1. TOP LOGO ZONE */}
      <View className="items-center mt-14 w-64 h-64 justify-center">
        {platformSettings?.siteLogo && (
          <Image
            source={{ uri: platformSettings.siteLogo }}
            className="w-48 h-48 relative right-2"
            resizeMode="contain"
          />
        )}
      </View>

      {/* 2. MIDDLE FORM ZONE */}
      <View className="flex-1 items-center px-6 pt-2 w-full">
        <Text className="text-center text-4xl font-bold">Sign In</Text>

        <Text className="text-center mt-2 text-lg text-gray-500">
          Never miss any important info!
        </Text>

        <View className="w-full mt-6 gap-4">
          <TextInput
            placeholder="Username or Email"
            value={usernameOrEmail}
            onChangeText={setUsernameOrEmail}
            keyboardType="default"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isSubmitting}
            returnKeyType="next"
            className="border border-gray-300 rounded-xl w-full py-4 px-5 bg-gray-200"
          />

          {/* PASSWORD INPUT WITH EYE ICON */}
          <View className="flex-row items-center border border-gray-300 rounded-xl w-full bg-gray-200 px-5">
            <TextInput
              placeholder="Password"
              placeholderTextColor="#6B7280"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!isPasswordVisible}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isSubmitting}
              returnKeyType="go"
              onSubmitEditing={handleLogin}
              style={{
                flex: 1,
                color: "#111827",
                height: 56,
                paddingVertical: 0,
              }}
            />

            <TouchableOpacity
              onPress={() => setIsPasswordVisible((visible) => !visible)}
              activeOpacity={0.7}
              hitSlop={10}
              accessibilityRole="button"
              accessibilityLabel={
                isPasswordVisible ? "Hide password" : "Show password"
              }
            >
              {isPasswordVisible ? (
                <EyeOff size={22} color="#6B7280" />
              ) : (
                <Eye size={22} color="#6B7280" />
              )}
            </TouchableOpacity>
          </View>

          {/* ERROR MESSAGE */}
          {error && <Text className="text-red-600 text-sm">{error}</Text>}
        </View>
      </View>

      {/* 3. BOTTOM CTA ZONE */}
      <View className="w-full px-6 pb-24 items-center">
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={handleLogin}
          disabled={isSubmitting}
          className={`w-full py-4 rounded-2xl items-center justify-center ${
            isSubmitting ? "bg-blue-400" : "bg-[#1d4f8f]"
          }`}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text className="text-white text-2xl font-bold tracking-wide">
              Sign In
            </Text>
          )}
        </TouchableOpacity>

        <Text className="text-gray-600 font-medium text-sm mt-4 text-center">
          Built for AASTU freshmen
        </Text>
      </View>
    </SafeAreaView>
  );
}
