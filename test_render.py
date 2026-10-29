"""
Quick test: Generate a sample handwritten PDF matching real notebook style.
No Gemini API key needed for this test.
"""

import sys
sys.path.insert(0, ".")

from handwriting_generator import generate_handwritten_pdf

SAMPLE_TEXT = """Q1. Explain the differences between hot working and cold working processes. State their advantages and limitations.

Hot working and cold working are metal forming processes. In both, force changes the shape of metal by plastic deformation without removing material.

Hot working is done above the metal's recrystallization temperature. New grains form during deformation, so the metal remains ductile and does not build up much strain hardening. Large shape changes need less force. Hot working is useful for forging and hot rolling.

Its limitations are the energy needed for heating, oxidation or scale on the surface, poorer dimensional accuracy and finish, and faster die wear.

Cold working is done below the recrystallization temperature, usually near room temperature. It makes the metal stronger and harder through strain hardening. It gives a smooth finish, close dimensions and no heating scale. Cold rolling and wire drawing are examples.

Cold working needs higher forces and allows less deformation in one step. It can leave residual stresses, stretch grains in the working direction and reduce ductility, so annealing may be needed.

In short, hot working suits large shape changes and improved ductility; cold working suits accurate, strong parts with a smooth surface.

Q2. What is the difference between a stack and a queue?

Ans 2. A stack follows the LIFO (Last In, First Out) principle, where the last element added is the first one removed. Think of a stack of plates.

A queue follows the FIFO (First In, First Out) principle, where the first element added is the first one removed. Think of a line at a ticket counter.

Key Operations:
- Stack: push (add to top), pop (remove from top)
- Queue: enqueue (add to rear), dequeue (remove from front)

Time Complexity for both: O(1) for insertion and deletion operations.
"""

if __name__ == "__main__":
    print("\nTest: Generating notebook-style handwritten PDF...\n")
    
    pdf_path = generate_handwritten_pdf(
        text=SAMPLE_TEXT,
        output_filename="test_notebook.pdf",
        subject="Manufacturing Processes",
        include_header=True,
    )
    
    print(f"\nDone! Open the PDF: {pdf_path}\n")
