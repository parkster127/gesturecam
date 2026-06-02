#!/usr/bin/env python3
"""
Ver Huella Facial - Visualiza tu embedding como vector
"""

import json
import sys

import numpy as np


def view_user_embedding(user_id=None):
    """Ver la huella facial de un usuario"""

    # Cargar base de datos
    try:
        with open("users_database.json") as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró users_database.json")
        print("Primero debes registrarte con: python3 user_registration.py --register")
        return

    if not db:
        print("❌ No hay usuarios registrados")
        return

    # Si no se especifica usuario, mostrar todos
    if user_id is None:
        print("\n" + "=" * 70)
        print("USUARIOS REGISTRADOS")
        print("=" * 70)
        for uid, data in db.items():
            print(f"\n👤 {data['name']} (ID: {uid})")
            print(f"   Embeddings: {len(data['embeddings'])}")
            print(f"   Registrado: {data['metadata']['registered_at']}")

        print("\nPara ver la huella facial de un usuario:")
        print("python3 view_embedding.py <user_id>")
        return

    # Mostrar usuario específico
    if user_id not in db:
        print(f"❌ Usuario '{user_id}' no encontrado")
        print(f"Usuarios disponibles: {', '.join(db.keys())}")
        return

    user = db[user_id]
    embeddings = [np.array(emb) for emb in user["embeddings"]]

    print("\n" + "=" * 70)
    print(f"HUELLA FACIAL DE: {user['name']}")
    print("=" * 70)

    print(f"\nID: {user_id}")
    print(f"Número de muestras: {len(embeddings)}")
    print(f"Dimensiones del vector: {len(embeddings[0])}")

    # Calcular embedding promedio
    avg_embedding = np.mean(embeddings, axis=0)

    print("\n" + "-" * 70)
    print("TU HUELLA FACIAL (Vector Promedio de 128 dimensiones)")
    print("-" * 70)

    # Mostrar en bloques de 8 números por línea
    for i in range(0, len(avg_embedding), 8):
        chunk = avg_embedding[i : i + 8]
        values = ", ".join([f"{v:+.4f}" for v in chunk])
        print(f"[{i:3d}-{i + 7:3d}]: {values}")

    print("\n" + "-" * 70)
    print("ESTADÍSTICAS DEL VECTOR")
    print("-" * 70)

    print(f"Magnitud (norma L2): {np.linalg.norm(avg_embedding):.6f}")
    print(f"Valor mínimo: {np.min(avg_embedding):+.6f}")
    print(f"Valor máximo: {np.max(avg_embedding):+.6f}")
    print(f"Valor promedio: {np.mean(avg_embedding):+.6f}")
    print(f"Desviación estándar: {np.std(avg_embedding):.6f}")

    # Distribución
    positive = np.sum(avg_embedding > 0)
    negative = np.sum(avg_embedding < 0)
    print(f"\nDistribución: {positive} positivos, {negative} negativos")

    # Variabilidad entre muestras
    print("\n" + "-" * 70)
    print("VARIABILIDAD ENTRE MUESTRAS")
    print("-" * 70)

    # Calcular similitud entre todas las muestras
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            sim = np.dot(embeddings[i], embeddings[j])
            similarities.append(sim)

    if similarities:
        print(f"Similitud promedio entre tus muestras: {np.mean(similarities):.4f}")
        print(f"Similitud mínima: {np.min(similarities):.4f}")
        print(f"Similitud máxima: {np.max(similarities):.4f}")
        print(
            f"Consistencia: {'✅ Alta' if np.mean(similarities) > 0.85 else '⚠️ Media' if np.mean(similarities) > 0.75 else '❌ Baja'}"
        )

    # Componentes principales
    print("\n" + "-" * 70)
    print("COMPONENTES MÁS IMPORTANTES")
    print("-" * 70)

    # Índices con mayores valores absolutos
    abs_values = np.abs(avg_embedding)
    top_indices = np.argsort(abs_values)[-10:][::-1]

    print("\nTop 10 dimensiones más distintivas:")
    for idx in top_indices:
        print(f"  Dimensión {idx:3d}: {avg_embedding[idx]:+.6f}")

    print("\n" + "=" * 70)
    print("\n✨ Esta es tu HUELLA FACIAL ÚNICA ✨")
    print("\nEste vector de 128 números es como tu 'DNI facial':")
    print("• Es único para ti")
    print("• No se puede reconstruir tu foto desde él")
    print("• Se usa para reconocerte comparando similitud con otros vectores")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    view_user_embedding(user_id)
