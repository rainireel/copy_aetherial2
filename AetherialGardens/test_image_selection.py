#!/usr/bin/env python3
"""
Test script to verify the image selection functionality works independently.
"""

import os
import sys
import tkinter as tk
import tkinter.filedialog
from typing import Optional

def test_file_dialog():
    """Test the file dialog functionality independently."""
    print("Testing file dialog functionality...")
    
    try:
        # Initialize tkinter root window (hidden)
        root = tk.Tk()
        root.withdraw()
        
        # Set the dialog to open in the user's home directory by default
        initial_dir = os.path.expanduser("~")
        
        print(f"Opening file dialog in: {initial_dir}")
        print("Please select an image file (PNG, JPG, JPEG, or BMP)...")
        
        # Open file dialog with supported image formats
        file_path = tkinter.filedialog.askopenfilename(
            title="Select an image for your puzzle",
            initialdir=initial_dir,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        # Clean up tkinter
        root.destroy()
        
        # Check if a file was selected
        if not file_path:
            print("No file selected (dialog was cancelled or closed)")
            return None
            
        print(f"Selected file: {file_path}")
        
        # Verify file extension
        SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp']
        _, ext = os.path.splitext(file_path.lower())
        if ext not in SUPPORTED_FORMATS:
            print(f"Unsupported file format: {ext}")
            return None
            
        # Verify file exists
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return None
            
        print("File selection successful!")
        return file_path
        
    except Exception as e:
        print(f"Error in file selection: {e}")
        return None

if __name__ == "__main__":
    print("Testing image selection functionality...")
    selected_file = test_file_dialog()
    
    if selected_file:
        print(f"\nSUCCESS: File selected: {selected_file}")
        print("The image selection functionality works correctly!")
    else:
        print("\nFile selection was cancelled or failed.")
        print("This could be due to:")
        print("1. Dialog was cancelled")
        print("2. Unsupported file format") 
        print("3. Environment-specific compatibility issues")