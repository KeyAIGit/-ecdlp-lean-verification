#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <future>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

struct Point {
  int x = 0;
  int y = 0;
  bool inf = true;
};

struct CaseDef { int p, n, gx, gy; };
struct Result {
  int p, n;
  long long exponent_pairs;
  long long c_values;
  long long outside_square_classes;
  long long candidate_formulas;
  long long exact_decoders;
  bool x_nonzero;
  bool y_nonzero;
  double seconds;
};

static int mod(long long x, int p) { x %= p; return x < 0 ? int(x + p) : int(x); }
static long long mod_pow(long long a, long long e, int p) {
  long long r = 1; a %= p;
  while (e) { if (e & 1) r = r * a % p; a = a * a % p; e >>= 1; }
  return r;
}
static int inv(int a, int p) { return int(mod_pow(a, p - 2, p)); }
static int legendre(int a, int p) {
  a = mod(a, p); if (!a) return 0;
  return mod_pow(a, (p - 1) / 2, p) == 1 ? 1 : -1;
}
static Point add(Point P, Point Q, int p) {
  if (P.inf) return Q;
  if (Q.inf) return P;
  if (P.x == Q.x && mod(P.y + Q.y, p) == 0) return {};
  int slope;
  if (P.x == Q.x && P.y == Q.y) {
    if (P.y == 0) return {};
    slope = mod(3LL * P.x * P.x * inv(mod(2LL * P.y, p), p), p);
  } else {
    slope = mod(1LL * (Q.y - P.y) * inv(mod(Q.x - P.x, p), p), p);
  }
  int x3 = mod(1LL * slope * slope - P.x - Q.x, p);
  int y3 = mod(1LL * slope * (P.x - x3) - P.y, p);
  return {x3, y3, false};
}
static long long key(Point P, int p) {
  if (P.inf) return -1;
  return 1LL * P.x * p + P.y;
}
static int cube_root(int p) {
  for (int seed = 2; seed < p; ++seed) {
    int beta = int(mod_pow(seed, (p - 1) / 3, p));
    if (beta != 1 && mod_pow(beta, 3, p) == 1) return beta;
  }
  throw std::runtime_error("cube root missing");
}

static Result run_case(CaseDef d) {
  auto start = std::chrono::steady_clock::now();
  Point G{d.gx, d.gy, false};
  std::vector<Point> pts(d.n);
  pts[0] = {};
  Point cur{};
  std::unordered_map<long long, int> scalar;
  scalar.reserve(2 * d.n);
  scalar[key(pts[0], d.p)] = 0;
  for (int k = 1; k < d.n; ++k) {
    cur = add(cur, G, d.p); pts[k] = cur; scalar[key(cur, d.p)] = k;
  }
  if (!add(cur, G, d.p).inf) throw std::runtime_error("bad order");
  int beta = cube_root(d.p);
  Point phiG{mod(1LL * beta * G.x, d.p), G.y, false};
  int lam = scalar.at(key(phiG, d.p));
  int lam2 = int(1LL * lam * lam % d.n);
  if ((1 + lam + lam2) % d.n) throw std::runtime_error("bad GLV root");

  int N = d.n - 1;
  std::vector<int> x(N), y(N), target(N), xc(N), yc(N);
  bool x_nonzero = true, y_nonzero = true;
  for (int k = 1; k < d.n; ++k) {
    x[k-1] = pts[k].x; y[k-1] = pts[k].y;
    x_nonzero &= x[k-1] != 0; y_nonzero &= y[k-1] != 0;
    long long total = 1LL * k + (1LL * lam * k % d.n) + (1LL * lam2 * k % d.n);
    if (total != d.n && total != 2LL * d.n) throw std::runtime_error("bad carry");
    target[k-1] = total == 2LL * d.n ? 1 : -1;
    xc[k-1] = legendre(x[k-1], d.p); yc[k-1] = legendre(y[k-1], d.p);
  }
  if (!x_nonzero || !y_nonzero) throw std::runtime_error("screen requires nonzero coordinates");

  std::vector<int8_t> chi(d.p); chi[0] = 0;
  for (int a = 1; a < d.p; ++a) chi[a] = int8_t(legendre(a, d.p));
  std::vector<int8_t> table(size_t(d.p) * d.p);
  for (int m = 0; m < d.p; ++m)
    for (int c = 0; c < d.p; ++c)
      table[size_t(m) * d.p + c] = chi[(1 + 1LL * c * m) % d.p];

  int E = d.p - 1;
  std::vector<std::vector<int>> xp(E, std::vector<int>(N));
  std::vector<std::vector<int>> yp(E, std::vector<int>(N));
  for (int i = 0; i < N; ++i) {
    xp[0][i] = yp[0][i] = 1;
    for (int a = 1; a < E; ++a) xp[a][i] = int(1LL * xp[a-1][i] * x[i] % d.p);
    for (int b = 1; b < E; ++b) yp[b][i] = int(1LL * yp[b-1][i] * y[i] % d.p);
  }
  std::vector<std::array<int8_t,8>> wanted(N);
  for (int i = 0; i < N; ++i) {
    int bit = 0;
    for (int u = 0; u < 2; ++u)
      for (int v = 0; v < 2; ++v)
        for (int sign = 0; sign < 2; ++sign)
          wanted[i][bit++] = int8_t(target[i] * (u ? xc[i] : 1) *
                                    (v ? yc[i] : 1) * (sign ? -1 : 1));
  }

  long long solutions = 0;
  std::vector<int> mval(N);
  for (int a = 0; a < E; ++a) {
    for (int b = 0; b < E; ++b) {
      for (int i = 0; i < N; ++i) mval[i] = int(1LL * xp[a][i] * yp[b][i] % d.p);
      for (int c = 0; c < d.p; ++c) {
        unsigned mask = 255;
        for (int i = 0; i < N && mask; ++i) {
          int q = table[size_t(mval[i]) * d.p + c];
          if (!q) { mask = 0; break; }
          unsigned next = 0;
          for (int j = 0; j < 8; ++j) if (q == wanted[i][j]) next |= (1u << j);
          mask &= next;
        }
        solutions += __builtin_popcount(mask);
      }
    }
  }
  long long pairs = 1LL * E * E;
  long long c_values = 1LL * d.p * pairs;
  long long formulas = 8LL * c_values;
  double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  return {d.p,d.n,pairs,c_values,8,formulas,solutions,x_nonzero,y_nonzero,seconds};
}

int main() {
  const std::array<CaseDef,4> cases{{
    {43,31,2,12}, {79,67,1,18}, {907,967,2,165}, {1087,271,1017,688}
  }};
  std::vector<std::future<Result>> jobs;
  for (auto c : cases) jobs.push_back(std::async(std::launch::async, run_case, c));
  std::cout << "{\n  \"schema_version\": 1,\n  \"cases\": [\n";
  for (size_t i=0;i<jobs.size();++i) {
    Result r=jobs[i].get();
    std::cout << "    {\"p\":"<<r.p<<",\"n\":"<<r.n
      <<",\"exponent_pairs\":"<<r.exponent_pairs
      <<",\"c_values\":"<<r.c_values
      <<",\"outside_square_classes\":"<<r.outside_square_classes
      <<",\"candidate_formulas\":"<<r.candidate_formulas
      <<",\"exact_decoders\":"<<r.exact_decoders
      <<",\"x_nonzero\":"<<(r.x_nonzero?"true":"false")
      <<",\"y_nonzero\":"<<(r.y_nonzero?"true":"false")
      <<",\"seconds\":"<<r.seconds<<"}"<<(i+1==jobs.size()?"\n":",\n");
  }
  std::cout << "  ],\n  \"claim_boundary\": \"toy-only exhaustive evaluation; no secp256k1 target and no decoder claim\"\n}\n";
}
