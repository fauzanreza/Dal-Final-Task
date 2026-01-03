#!/usr/bin/env python3
import sys
from collections import defaultdict, deque

def solve():
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return
    it = iter(data)
    n = next(it); m = next(it)

    b = [0]*n
    e = [0]*n
    for i in range(n):
        b[i] = next(it)
        e[i] = next(it)

    U = [0]*m
    V = [0]*m
    adj = [[] for _ in range(n)]
    for eid in range(m):
        x = next(it) - 1
        y = next(it) - 1
        U[eid] = x
        V[eid] = y
        adj[x].append((y, eid))
        adj[y].append((x, eid))

    # ---------- find bridges (iterative DFS) ----------
    tin = [-1]*n
    low = [0]*n
    parent = [-1]*n
    parent_e = [-1]*n
    is_bridge = [False]*m
    timer = 0

    for root in range(n):
        if tin[root] != -1:
            continue
        stack = [(root, 0)]
        parent[root] = -1
        parent_e[root] = -1

        while stack:
            v, idx = stack[-1]
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1

            if idx < len(adj[v]):
                to, eid = adj[v][idx]
                stack[-1] = (v, idx + 1)

                if eid == parent_e[v]:
                    continue
                if tin[to] == -1:
                    parent[to] = v
                    parent_e[to] = eid
                    stack.append((to, 0))
                else:
                    # back edge
                    low[v] = min(low[v], tin[to])
            else:
                stack.pop()
                p = parent[v]
                if p != -1:
                    pe = parent_e[v]
                    low[p] = min(low[p], low[v])
                    if low[v] > tin[p]:
                        is_bridge[pe] = True

    # ---------- components in graph without bridges ----------
    comp_id = [-1]*n
    comps = []
    for i in range(n):
        if comp_id[i] != -1:
            continue
        cid = len(comps)
        q = [i]
        comp_id[i] = cid
        verts = []
        while q:
            v = q.pop()
            verts.append(v)
            for to, eid in adj[v]:
                if is_bridge[eid]:
                    continue
                if comp_id[to] == -1:
                    comp_id[to] = cid
                    q.append(to)
        comps.append(verts)

    comp_edge_cnt = [0]*len(comps)
    deg_nb = [0]*n
    for eid in range(m):
        if is_bridge[eid]:
            continue
        cid = comp_id[U[eid]]
        comp_edge_cnt[cid] += 1
        deg_nb[U[eid]] += 1
        deg_nb[V[eid]] += 1

    # ---------- helper: cyclic rotation check ----------
    def is_rotation(a, bseq):
        if len(a) != len(bseq):
            return False
        if not a:
            return True
        # KMP could be used; for simplicity use tuple + find on doubled list (OK for samples)
        A = a
        B = bseq
        dbl = A + A
        # naive scan
        L = len(A)
        for s in range(L):
            ok = True
            for j in range(L):
                if dbl[s+j] != B[j]:
                    ok = False
                    break
            if ok:
                return True
        return False

    # ---------- helper: build cycle order for simple cycle ----------
    def cycle_order(verts_set):
        start = next(iter(verts_set))
        # each vertex has degree 2 in this component
        nbs = [to for to, eid in adj[start] if (not is_bridge[eid]) and (to in verts_set)]
        prev = start
        cur = nbs[0]
        order = [start]
        while cur != start:
            order.append(cur)
            nbs2 = [to for to, eid in adj[cur] if (not is_bridge[eid]) and (to in verts_set)]
            nxt = nbs2[0] if nbs2[0] != prev else nbs2[1]
            prev, cur = cur, nxt
        return order

    # ---------- helper: parity of required permutation (only if all labels distinct) ----------
    def required_parity_even(verts):
        k = len(verts)
        loc = {v:i for i,v in enumerate(verts)}
        b_loc = [b[v] for v in verts]
        e_loc = [e[v] for v in verts]
        if len(set(b_loc)) != k:
            return True  # duplicates -> can flip parity by swapping equal labels
        pos_final = {e_loc[i]: i for i in range(k)}
        p = [pos_final[b_loc[i]] for i in range(k)]
        vis = [False]*k
        cycles = 0
        for i in range(k):
            if not vis[i]:
                cycles += 1
                x = i
                while not vis[x]:
                    vis[x] = True
                    x = p[x]
        # parity even iff (k - cycles) is even
        return ((k - cycles) % 2) == 0

    # ---------- helper: cactus / even-cycle detection within component ----------
    def component_type(verts, cid):
        # returns (any_perm, only_even) with any_perm True => always ok
        # Assumes component is not a simple cycle.
        verts_set = set(verts)

        tin2 = [-1]*n
        par = [-1]*n
        pare = [-1]*n
        in_cycle_edge = [False]*m  # edges in this component only will ever be set
        t = 0
        non_cactus = False
        has_even_cycle = False

        root = verts[0]
        stack = [(root, 0)]
        tin2[root] = t; t += 1
        par[root] = -1; pare[root] = -1

        while stack and not non_cactus:
            v, idx = stack[-1]
            # advance neighbors
            neighs = adj[v]
            if idx < len(neighs):
                to, eid = neighs[idx]
                stack[-1] = (v, idx + 1)

                if is_bridge[eid] or (to not in verts_set):
                    continue

                if tin2[to] == -1:
                    tin2[to] = t; t += 1
                    par[to] = v
                    pare[to] = eid
                    stack.append((to, 0))
                elif to != par[v] and tin2[to] < tin2[v]:
                    # back edge v -> to (ancestor): extract cycle along parent pointers
                    length = 1
                    edges_on_cycle = [eid]
                    cur = v
                    while cur != to:
                        pe = pare[cur]
                        if pe == -1:
                            break
                        if in_cycle_edge[pe]:
                            non_cactus = True
                            break
                        edges_on_cycle.append(pe)
                        in_cycle_edge[pe] = True
                        length += 1
                        cur = par[cur]
                    if non_cactus:
                        break
                    if in_cycle_edge[eid]:
                        non_cactus = True
                        break
                    in_cycle_edge[eid] = True
                    if length % 2 == 0:
                        has_even_cycle = True
            else:
                stack.pop()

        if non_cactus:
            return (True, False)          # any permutation achievable
        if has_even_cycle:
            return (True, False)          # cactus + some even cycle => any permutation
        return (False, True)              # cactus + all odd cycles => only even permutations

    # ---------- solve per component ----------
    for cid, verts in enumerate(comps):
        # per-component multiset must match because bridges can't be used at all [web:38]
        bc = sorted(b[v] for v in verts)
        ec = sorted(e[v] for v in verts)
        if bc != ec:
            print("impossible")
            return

        k = len(verts)
        ecnt = comp_edge_cnt[cid]

        # isolated vertex (or component with no non-bridge edges): must already match per vertex
        if ecnt == 0:
            for v in verts:
                if b[v] != e[v]:
                    print("impossible")
                    return
            continue

        # simple cycle check
        if ecnt == k and all(deg_nb[v] == 2 for v in verts):
            order = cycle_order(set(verts))
            init_seq = [b[v] for v in order]
            final_seq = [e[v] for v in order]
            if not is_rotation(init_seq, final_seq):
                print("impossible")
                return
            continue

        any_perm, only_even = component_type(verts, cid)
        if any_perm:
            continue
        # only even permutations allowed
        if not required_parity_even(verts):
            print("impossible")
            return

    print("possible")


if __name__ == "__main__":
    solve()

