import sqlite3
import numpy as np

class FaceDB:
    def __init__(self, db_path="face_db.db"):
        """
        Initialize the database connection and create tables if they don't exist.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        self.embeddings_matrix = None
        self.person_ids_array = None
        self.persons_data = None

    def _create_tables(self):
        """
        Create persons and embeddings tables in the database.
        """
        c = self.conn.cursor()
        # Table for person information
        c.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            other_info TEXT
        )
        """)
        # Table for embeddings with foreign key to persons
        c.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            FOREIGN KEY (person_id) REFERENCES persons(id)
        )
        """)
        self.conn.commit()

    def add_person(self, name, age=None, other_info=None):
        """
        Add a new person to the database.
        Returns the new person's ID.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO persons (name, age, other_info) VALUES (?, ?, ?)",
                  (name, age, other_info))
        self.conn.commit()
        return c.lastrowid

    def add_embedding(self, person_id, embedding, load=True):
        """
        Add a face embedding for a specific person.
        Embedding is stored as a BLOB.
        """
        c = self.conn.cursor()
        embedding_blob = embedding.astype(np.float32).tobytes()
        c.execute("INSERT INTO embeddings (person_id, embedding) VALUES (?, ?)",
                  (person_id, embedding_blob))
        self.conn.commit()
        if load:
            self.load_embeddings()

    def load_embeddings(self):
        """
        Load all embeddings into a single matrix and maintain index-person mapping.
        """
        c = self.conn.cursor()
        c.execute("SELECT embedding, person_id FROM embeddings")
        rows = c.fetchall()

        embeddings_list = []
        person_ids_list = []

        for blob, person_id in rows:
            emb = np.frombuffer(blob, dtype=np.float32)
            embeddings_list.append(emb)
            person_ids_list.append(person_id)

        if embeddings_list:
            self.embeddings_matrix = np.vstack(embeddings_list)
            self.person_ids_array = np.array(person_ids_list)
        else:
            self.embeddings_matrix = np.empty((0, 512), dtype=np.float32)
            self.person_ids_array = np.array([], dtype=int)

        # Load person info
        c.execute("SELECT id, name, age, other_info FROM persons")
        self.persons_data = {row[0]: {"name": row[1], "age": row[2], "other_info": row[3]} for row in c.fetchall()}

    def identify_face(self, new_embedding, threshold=0.5):
        """
        Identify the person for a new embedding using cosine similarity.
        Returns person info and similarity score.
        """
        if self.embeddings_matrix is None or self.person_ids_array is None:
            raise ValueError("Embeddings not loaded. Call load_embeddings() first.")

        # Normalize embeddings
        new_emb_norm = new_embedding / np.linalg.norm(new_embedding)
        db_norm = self.embeddings_matrix / np.linalg.norm(self.embeddings_matrix, axis=1, keepdims=True)
        if len(self.embeddings_matrix) == 0:
            return {"name": "Unknown"}, 0

        # Cosine similarity vectorized
        sims = np.dot(db_norm, new_emb_norm)
        best_idx = np.argmax(sims)
        best_score = sims[best_idx]

        if best_score >= threshold:
            best_person_id = self.person_ids_array[best_idx]
            person_info = self.persons_data[best_person_id]
            return person_info, best_score
        else:
            return {"name": "Unknown"}, best_score

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
