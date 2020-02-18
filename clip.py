if __name__ == "__main__":
    # Initialize global variables, create output dirs
    import app.init
    import app.download
    import app.clipmodifier
    # Download the full video
    app.download.main()
    # Generate clips from the full video
    app.clipmodifier.main()