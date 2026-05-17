import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { Text, View, StyleSheet } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginScreen } from './screens/LoginScreen';
import { DashboardScreen } from './screens/DashboardScreen';
import { GradesScreen } from './screens/GradesScreen';
import { ScheduleScreen } from './screens/ScheduleScreen';
import { ProfileScreen } from './screens/ProfileScreen';

const Tab = createBottomTabNavigator();
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={{
            tabBarActiveTintColor: '#1677ff',
            headerStyle: { backgroundColor: '#1677ff' },
            headerTintColor: 'white',
          }}
        >
          <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Bosh sahifa' }} />
          <Tab.Screen name="Grades" component={GradesScreen} options={{ title: 'Baholar' }} />
          <Tab.Screen name="Schedule" component={ScheduleScreen} options={{ title: 'Jadval' }} />
          <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profil' }} />
        </Tab.Navigator>
      </NavigationContainer>
    </QueryClientProvider>
  );
}
