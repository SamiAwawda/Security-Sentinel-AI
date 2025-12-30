"""
AGKS - Akıllı Gözetim Koruma Sistemi
Main application runner
"""

from app import create_app
import sys

def main():
    """Initialize and run the Flask application"""
    try:
        # Create Flask app using factory pattern
        app = create_app()
        
        # Run the application
        print("\n" + "=" * 50)
        print("🛡️  AGKS - Akıllı Gözetim Koruma Sistemi")
        print("=" * 50)
        print("📡 Server starting...")
        print("📡 Access dashboard at: http://localhost:5000")
        print("=" * 50 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,  # Prevent camera conflicts
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
