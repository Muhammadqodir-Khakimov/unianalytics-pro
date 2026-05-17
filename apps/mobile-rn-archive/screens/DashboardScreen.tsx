import { View, Text, ScrollView, StyleSheet } from 'react-native';

export function DashboardScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.hero}>
        <Text style={styles.heroTitle}>Salom, Talaba!</Text>
        <Text style={styles.heroSubtitle}>Sizning hisobingiz tayyor</Text>
      </View>

      <View style={styles.kpiRow}>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiLabel}>GPA</Text>
          <Text style={styles.kpiValue}>3.45</Text>
        </View>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiLabel}>Davomat</Text>
          <Text style={styles.kpiValue}>87%</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>So'nggi baholar</Text>
        <Text>Matematik analiz: 85</Text>
        <Text>Algoritmlar: 72</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f7fa' },
  hero: { backgroundColor: '#1677ff', padding: 24 },
  heroTitle: { color: 'white', fontSize: 24, fontWeight: 'bold' },
  heroSubtitle: { color: 'white', opacity: 0.9, marginTop: 4 },
  kpiRow: { flexDirection: 'row', padding: 12, gap: 12 },
  kpiCard: { flex: 1, backgroundColor: 'white', padding: 16, borderRadius: 12 },
  kpiLabel: { color: '#666', fontSize: 12 },
  kpiValue: { fontSize: 28, fontWeight: 'bold', marginTop: 4 },
  card: { margin: 12, backgroundColor: 'white', padding: 16, borderRadius: 12 },
  cardTitle: { fontSize: 16, fontWeight: '600', marginBottom: 8 },
});
