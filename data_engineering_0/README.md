# Serverless ETL: A Beginner's Guide
## Building the "Plumbing" of the Internet

![Stack](https://img.shields.io/badge/Platform-Cloudflare_Workers-orange?logo=cloudflare)
![Stack](https://img.shields.io/badge/Language-TypeScript-3178C6?logo=typescript)
![Stack](https://img.shields.io/badge/Database-D1_SQLite-blue?logo=sqlite)

---

## **The Problem: The Water Treatment Plant**

Imagine you are building a city. You need to get water to every house.
- **Raw Data** is the dirty river water. You can't drink it.
- **The Database** is the clean water tank in the house.
- **Data Engineering** is the treatment plant and the pipes in between.

You need to:
1.  **Extract**: Pump water from the river.
2.  **Transform**: Filter out the mud and add chlorine.
3.  **Load**: Pump it into the house's tank.

If the pipes are slow (Latency), the shower has no pressure. If the pipes leak (Data Loss), the house floods.

---

## **The Solution: Edge Computing**

Traditionally, you have one giant treatment plant (Central Server). If you live far away, water takes forever to arrive.

**Cloudflare Workers** are like putting a mini-treatment plant on every street corner.
- **Edge Computing:** The code runs physically close to the user.
- **Serverless:** You don't manage the plant; you just write the instructions for filtering.

This project builds a high-speed **ETL Pipeline** that runs on the "Edge".

---

## **Features**

- **Ingestion API**: A high-performance endpoint to accept JSON data (The River Pump).
- **Validation**: Checks if the data is "clean" (The Filter).
- **Storage**: Saves to Cloudflare D1 (SQLite) (The Tank).
- **Analytics**: A dashboard to see how much water is flowing.

---

## **How to Use the Lab**

### **Step 1: The Setup**
We use **Wrangler**, the CLI tool for Cloudflare. It lets us simulate the entire internet on our laptop.

### **Step 2: Send Data (The Extract)**
You can send a "packet" of data to the worker.
```bash
curl -X POST http://localhost:8787/api/ingest -d '{"sensor_id": 1, "temp": 22.5}'
```

### **Step 3: The Worker (The Transform)**
The code inside `src/index.ts` catches this packet.
- It checks: "Is `temp` a number?"
- It adds a timestamp: "When did this arrive?"

### **Step 4: The Database (The Load)**
The worker saves it to D1. You can query it with SQL:
```sql
SELECT * FROM measurements WHERE temp > 20;
```

---

## **Key Takeaways for Interviews**

| Concept | Explanation |
|---|---|
| **ETL** | Extract, Transform, Load. The standard process for moving data. |
| **Serverless** | You write code, not config files. No "starting servers" or "patching OS". |
| **Edge Computing** | Running code in 300+ cities worldwide so it's fast for everyone. |
| **ACID** | Atomicity, Consistency, Isolation, Durability. Guarantees that if the database says "Saved", it is actually saved. |

---

## **Tech Stack**
- **Runtime**: Cloudflare Workers (V8 Engine)
- **Language**: TypeScript
- **Database**: Cloudflare D1 (Distributed SQLite)
- **IaC**: Wrangler (Infrastructure as Code)

## **Getting Started**

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Local Server**
   ```bash
   npm run dev
   ```

3. **Deploy to Edge**
   ```bash
   npm run deploy
   ```

## License
MIT
