# Neo4j AuraDB Environment Setup

## Quick Setup for PowerShell

```powershell
# Set environment variables in PowerShell (replace with your actual values)
$env:NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="your-password"

# Verify they're set
echo "URI: $env:NEO4J_URI"
echo "Username: $env:NEO4J_USERNAME"
echo "Password: [HIDDEN]"
```

## Alternative: Create .env file

Create a file named `.env` in the kg_creation directory:

```
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

## Run the Import

```bash
# Test connection first
python auradb_test.py

# If connection works, run import
python auradb_import.py
```

## Troubleshooting

1. **Check your AuraDB instance is running**
2. **Verify credentials are correct**
3. **Ensure firewall allows connections**
4. **Check if your IP is whitelisted in AuraDB console**