import sys
from collections import deque
from pathlib import Path
from typing import List, Tuple
import random, time

def myers_diff_distance(a: str, b: str) -> int:
    N = len(a)
    M = len(b)
    MAX = N + M;
    v = {1: 0}
    for D in range(MAX + 1):
        for k in range(-D, D + 1, 2): # diagonals k ∈ {−D,−D+2,…,D−2,D}
            if k == -D or (k != D and v.get(k - 1, 0) < v.get(k + 1, 0)):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1
            y = x - k
            while x < N and y < M and a[x] == b[y]:
                x += 1
                y += 1
            v[k] = x
            if x >= N and y >= M:
                return D
    return -1

def find_middle_snake(a: str, b: str) -> Tuple[int, int, int, int]:
    N, M = len(a), len(b)
    delta = N - M
    max_d = (N + M + 1) // 2
    v_f = {1: 0}
    v_r = {delta - 1: N}

    for D in range(max_d + 1):
        # ----- forward search -----
        for k in range(-D, D + 1, 2):
            
            if k == -D or (k != D and v_f.get(k - 1, 0) < v_f.get(k + 1, 0)):
                x = v_f.get(k + 1, 0)
            else:
                x = v_f.get(k - 1, 0) + 1
            y = x - k
            x_start = x
            y_start = x - k


            while x < N and y < M and a[x] == b[y]:
                x += 1
                y += 1
            v_f[k] = x

            if delta % 2 == 1 and (k >= delta - (D - 1) and k <= delta + (D - 1)):
                if v_f[k] >= v_r.get(k, -1):
                    return x_start, y_start, x, y

        # ----- reverse search -----
        for k in range(-D + delta, D + delta + 1, 2):
            if k == D + delta or (k != -D + delta and v_r.get(k - 1, N) < v_r.get(k + 1, N)):
                x = v_r.get(k - 1, N)
            else:
                x = v_r.get(k + 1, N) - 1
            y = x - k
            x_end, y_end = x, y

            while x > 0 and y > 0 and a[x - 1] == b[y - 1]:
                x -= 1
                y -= 1
            v_r[k] = x

            if delta % 2 == 0 and (k >= -D and k <= D):
                if v_f.get(k, 0) >= v_r[k]:
                    return x, y, x_end, y_end

    return -1, -1, -1, -1


def linear_space_lcs(a: str, b: str) -> List[str]:
    N, M = len(a), len(b)
    
    # Base Cases
    if N == 0 or M == 0:
        return []
    
    # If there is only 1 edit (or 0), the shorter string is the LCS
    if N > 0 and M > 0 and (N + M) <= 1:
        return list(a) if N < M else list(b)
        
    # Find the middle snake to split the problem
    x, y, u, v = find_middle_snake(a, b)
    
    if x == -1: # Failsafe
        return []
        
    left  = linear_space_lcs(a[:x], b[:y])
    middle = list(a[x:u])           # the snake (may be empty)
    right = linear_space_lcs(a[u:], b[v:])

    return left + middle + right

def lcs_iterative(a: List[str], b: List[str]) -> List[str]:
    work = deque([ (0, len(a), 0, len(b)) ])   # (a_start, a_end, b_start, b_end)
    
    # We will store tuples of (original_index_in_a, character)
    result_with_index: List[Tuple[int, str]] = []

    while work:
        a0, a1, b0, b1 = work.pop()
        sub_a = a[a0:a1]
        sub_b = b[b0:b1]

        # ----- base cases -----
        if not sub_a or not sub_b:
            continue
            
        if len(sub_a) == 1:
            if sub_a[0] in sub_b:
                # Save it with its exact index in string 'a'
                result_with_index.append((a0, sub_a[0]))
            continue
            
        if len(sub_b) == 1:
            if sub_b[0] in sub_a:
                # Find the exact index of the match within sub_a to maintain order
                idx_in_a = a0 + sub_a.index(sub_b[0])
                result_with_index.append((idx_in_a, sub_b[0]))
            continue

        # ----- split with middle snake -----
        x, y, u, v = find_middle_snake(sub_a, sub_b)
        
        if x == -1: # Failsafe
            continue

        # push left part
        work.append((a0, a0 + x, b0, b0 + y))
        
        # middle snake (may be empty)
        # Record each character of the snake with its absolute index!
        for i in range(x, u):
            result_with_index.append((a0 + i, sub_a[i]))
            
        # push right part
        work.append((a0 + u, a1, b0 + v, b1))

    # Sort all found characters by their original index in string 'a'
    result_with_index.sort(key=lambda item: item[0])

    # Extract just the characters in the newly sorted order
    return [char for idx, char in result_with_index]

def generate_diff(file_a: List[str], file_b: List[str], lcs: List[str]) -> List[str]:
    """Compares the original files against their LCS to generate a diff."""
    i = 0  # Pointer for file_a
    j = 0  # Pointer for file_b
    k = 0  # Pointer for lcs
    
    diff_output: List[str] = []

    # Continue until we have processed all lines in both files
    while i < len(file_a) or j < len(file_b):
        
        # 1. If both files match the current LCS line, it's an unchanged line.
        if k < len(lcs) and i < len(file_a) and j < len(file_b) and file_a[i] == lcs[k] and file_b[j] == lcs[k]:
            diff_output.append(f"  {file_a[i]}") # Note the two spaces for 'kept'
            i += 1
            j += 1
            k += 1
            
        # 2. If file_a has a line that doesn't match the LCS, it was deleted.
        elif i < len(file_a) and (k == len(lcs) or file_a[i] != lcs[k]):
            diff_output.append(f"- {file_a[i]}")
            i += 1
            
        # 3. If file_b has a line that doesn't match the LCS, it was added.
        elif j < len(file_b) and (k == len(lcs) or file_b[j] != lcs[k]):
            diff_output.append(f"+ {file_b[j]}")
            j += 1

    return diff_output

def read_entire_file(file_path: str) -> str:
    p = Path(file_path)
    return p.read_text()


def usage(program: str) -> None:
    print(f"Usage: {program} <file1> <fil2>")

def main() -> int:
    assert len(sys.argv) > 0
    program, *args = sys.argv
    if len(args) < 2:
        usage(program)
        return 1

    file_path1 = args[0]
    file_path2 = args[1]
    
    # Read files and split into lists of strings (lines)
    lines1 = read_entire_file(file_path1).splitlines()
    lines2 = read_entire_file(file_path2).splitlines()

    print(f"File 1 length: {len(lines1)} lines")
    print(f"File 2 length: {len(lines2)} lines")

    print("\nCalculating Line-by-Line LCS...")
    start_time = time.time()
    
    # Pass the lists of lines directly into your iterative function!
    lcs_lines = lcs_iterative(lines1, lines2)
    
    end_time = time.time()
    print(f"Found {len(lcs_lines)} matching lines in {end_time - start_time:.4f} seconds.")

    patch = generate_diff(lines1, lines2, lcs_lines)
    
    print("\n--- DIFF OUTPUT ---")
    for line in patch:
        print(line)

    return 0


if __name__ == '__main__':
    exit(main())