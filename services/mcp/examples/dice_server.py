#!/usr/bin/env python3
import random
import logging
from fastmcp import FastMCP

mcp = FastMCP(name="Dice Roller")

@mcp.tool
def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    logging.info(f"Rolling {n_dice} dice")   
    return [random.randint(1, 6) for _ in range(n_dice)]

if __name__ == "__main__":
    # Streamable HTTP on default port 8000
    mcp.run(transport="http", port=8000, stateless_http=True)
