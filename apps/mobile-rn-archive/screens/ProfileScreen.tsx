import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export function ProfileScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.avatar}><Text style={styles.avatarText}>👤</Text></View>
      <Text style={styles.name}>Talaba ismi</Text>
      <Text style={styles.email}>student@university.uz</Text>
      <View style={styles.statsRow}>
        <View style={styles.stat}><Text style={styles.statValue}>3.45</Text><Text style={styles.statLabel}>GPA</Text></View>
        <View style={styles.stat}><Text style={styles.statValue}>87%</Text><Text style={styles.statLabel}>Davomat</Text></View>
        <View style={styles.stat}><Text style={styles.statValue}>5/30</Text><Text style={styles.statLabel}>O'rin</Text></View>
      </View>
      <TouchableOpacity style={styles.btn}><Text style={styles.btnText}>Sozlamalar</Text></TouchableOpacity>
      <TouchableOpacity style={[styles.btn, styles.btnDanger]}><Text style={styles.btnText}>Chiqish</Text></TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, alignItems: 'center', backgroundColor: '#f5f7fa' },
  avatar: { width: 100, height: 100, borderRadius: 50, backgroundColor: '#1677ff', justifyContent: 'center', alignItems: 'center', marginTop: 24 },
  avatarText: { fontSize: 48 },
  name: { fontSize: 22, fontWeight: 'bold', marginTop: 16 },
  email: { color: '#666', marginTop: 4 },
  statsRow: { flexDirection: 'row', marginTop: 32, gap: 16 },
  stat: { backgroundColor: 'white', padding: 16, borderRadius: 12, minWidth: 80, alignItems: 'center' },
  statValue: { fontSize: 24, fontWeight: 'bold', color: '#1677ff' },
  statLabel: { color: '#666', fontSize: 12, marginTop: 4 },
  btn: { backgroundColor: '#1677ff', padding: 14, borderRadius: 8, marginTop: 16, width: '100%' },
  btnDanger: { backgroundColor: '#ef4444' },
  btnText: { color: 'white', textAlign: 'center', fontWeight: '600' },
});
