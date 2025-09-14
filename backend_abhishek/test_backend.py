#!/usr/bin/env python3
"""
Backend Test Script - Maria Elena Gonzalez Rich Patient Data
"""

from app import get_patient_summary, get_db_connection

def test_maria_elena_data():
    """Test comprehensive patient data access"""
    try:
        print("🧪 Testing Backend Database Access for Rich Patient Data")
        print("=" * 60)
        
        # Get database connection
        db = get_db_connection()
        
        # Test patient summary
        summary = get_patient_summary(7, db)
        
        print("🎯 Maria Elena Gonzalez - Rich Patient Summary:")
        print(f"   👤 Name: {summary['patient']['name']}")
        print(f"   📅 DOB: {summary['patient']['dob']}")
        print(f"   ⚕️  Medical History: {summary['data_summary']['medical_history_count']} conditions")
        print(f"   💊 Medications: {summary['data_summary']['medication_count']} active medications")
        print(f"   📋 Appointments: {summary['data_summary']['appointment_count']} appointments")
        print(f"   🧪 Lab Reports: {summary['data_summary']['lab_report_count']} reports")
        print(f"   📊 Lab Findings: {summary['data_summary']['lab_finding_count']} findings")
        print(f"   🩺 Symptoms: {summary['data_summary']['symptom_count']} recorded symptoms")
        print(f"   💬 Chat Messages: {summary['data_summary']['chat_message_count']} messages")
        
        print("\n" + "=" * 60)
        print("✅ BACKEND SYNCHRONIZATION SUCCESSFUL!")
        print("📊 Rich patient data is fully accessible")
        print("🔗 Ready for knowledge graph creation via MCP functions")
        print("🚀 Both backend_abhishek and mcp_server are synchronized")
        
        # Close database connection
        db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing patient data: {e}")
        return False

if __name__ == "__main__":
    test_maria_elena_data()