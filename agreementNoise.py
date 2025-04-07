import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random

n = 100  # Number of qubits
noise_probability = 0.05  # Probability of applying noise (5% chance)

#50% chance of eavesdropper being present
eve_is_present = random.random() < 0.5
print(f"Eve is {'present' if eve_is_present else 'absent'} in this run.")

# Alice: random bits and bases
alice_bits = np.random.randint(2, size=n)
alice_bases = np.random.randint(2, size=n)

# Bob: random bases
bob_bases = np.random.randint(2, size=n)

# Eve: random bases (but won't matter if Eve is absent)
eve_bases = np.random.randint(2, size=n)


circuits = []
for i in range(n):
    qc = QuantumCircuit(1, 1)


    if alice_bits[i] == 1:
        qc.x(0)
    if alice_bases[i] == 1:
        qc.h(0)

    # Add noise if Eve is absent
    if not eve_is_present:
        if random.random() < noise_probability:
            qc.x(0)  # Bit-flip noise

    # Eve intercepts all qubits if she's present
    if eve_is_present:
        if eve_bases[i] == 1:
            qc.h(0)  # Measure in X basis, will be right roughly 50% of the time
        qc.measure(0, 0)
        qc.reset(0)

        # Re-encode a random bit to simulate possible disturbance
        if np.random.rand() < 0.5:
            qc.x(0)
        if eve_bases[i] == 1:
            qc.h(0)

    # Bob measures
    if bob_bases[i] == 1:
        qc.h(0)
    qc.measure(0, 0)

    circuits.append(qc)

#Simulate QKD
simulator = AerSimulator()
job = simulator.run(circuits, shots=1, memory=True)
result = job.result()

#Bob’s measured bits
bob_results = [int(result.get_memory(i)[-1]) for i in range(n)]

#Key sifting- keep bits where Alice and Bob used the same basis, discard mismatched
matching_indices = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
alice_key = [int(alice_bits[i]) for i in matching_indices]
bob_key = [int(bob_results[i]) for i in matching_indices]

#Calculate Key Agreement Rate
agreement_count = sum(a == b for a, b in zip(alice_key, bob_key))
key_agreement_rate = agreement_count / len(alice_key)
print(f"\nKey Agreement Rate: {key_agreement_rate:.2%}")

#QBER
disagreement_count = sum(a != b for a, b in zip(alice_key, bob_key))
qber = disagreement_count / len(alice_key)
print(f"Quantum Bit Error Rate (QBER): {qber:.2%}")

#print other desirable info
print()
print("Alice's key:", alice_key)
print("Bob's key:  ", bob_key)
print("Key length:", len(alice_key))
accuracy = sum(a == b for a, b in zip(alice_key, bob_key)) / len(alice_key) * 100
print(f"Agreement: {accuracy:.2f}%")