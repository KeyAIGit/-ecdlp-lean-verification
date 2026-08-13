#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;
using i128 = __int128_t;

static u64 add_mod(u64 a, u64 b, u64 m) {
  u64 c = a + b;
  if (c >= m || c < a) c %= m;
  return c % m;
}
static u64 sub_mod(u64 a, u64 b, u64 m) {
  return a >= b ? a - b : m - (b - a);
}
static u64 mul_mod(u64 a, u64 b, u64 m) {
  return static_cast<u64>((u128)a * b % m);
}
static u64 pow_mod(u64 a, u64 e, u64 m) {
  u64 r = 1 % m;
  while (e) {
    if (e & 1) r = mul_mod(r, a, m);
    a = mul_mod(a, a, m);
    e >>= 1;
  }
  return r;
}
static u64 inv_mod(u64 a, u64 m) {
  i128 t = 0, new_t = 1;
  i128 r = static_cast<i128>(m), new_r = static_cast<i128>(a % m);
  while (new_r != 0) {
    i128 q = r / new_r;
    i128 next_t = t - q * new_t;
    t = new_t;
    new_t = next_t;
    i128 next_r = r - q * new_r;
    r = new_r;
    new_r = next_r;
  }
  if (r != 1) throw std::runtime_error("noninvertible field element");
  t %= static_cast<i128>(m);
  if (t < 0) t += m;
  return static_cast<u64>(t);
}

struct Jacobian {
  u64 x;
  u64 y;
  u64 z;
};
static const Jacobian O{1, 1, 0};

static Jacobian point_double(const Jacobian &point, u64 modulus) {
  if (point.z == 0 || point.y == 0) return O;
  u64 xx = mul_mod(point.x, point.x, modulus);
  u64 yy = mul_mod(point.y, point.y, modulus);
  u64 yyyy = mul_mod(yy, yy, modulus);
  u64 s = mul_mod(4 % modulus, mul_mod(point.x, yy, modulus), modulus);
  u64 m = mul_mod(3 % modulus, xx, modulus);
  u64 x3 = sub_mod(mul_mod(m, m, modulus), mul_mod(2 % modulus, s, modulus), modulus);
  u64 y3 = sub_mod(
      mul_mod(m, sub_mod(s, x3, modulus), modulus),
      mul_mod(8 % modulus, yyyy, modulus), modulus);
  u64 z3 = mul_mod(2 % modulus, mul_mod(point.y, point.z, modulus), modulus);
  return {x3, y3, z3};
}

static Jacobian point_add(const Jacobian &left, const Jacobian &right, u64 modulus) {
  if (left.z == 0) return right;
  if (right.z == 0) return left;
  u64 z1z1 = mul_mod(left.z, left.z, modulus);
  u64 z2z2 = mul_mod(right.z, right.z, modulus);
  u64 u1 = mul_mod(left.x, z2z2, modulus);
  u64 u2 = mul_mod(right.x, z1z1, modulus);
  u64 s1 = mul_mod(left.y, mul_mod(right.z, z2z2, modulus), modulus);
  u64 s2 = mul_mod(right.y, mul_mod(left.z, z1z1, modulus), modulus);
  if (u1 == u2) return s1 == s2 ? point_double(left, modulus) : O;
  u64 h = sub_mod(u2, u1, modulus);
  u64 two_h = mul_mod(2 % modulus, h, modulus);
  u64 i = mul_mod(two_h, two_h, modulus);
  u64 j = mul_mod(h, i, modulus);
  u64 r = mul_mod(2 % modulus, sub_mod(s2, s1, modulus), modulus);
  u64 v = mul_mod(u1, i, modulus);
  u64 r2 = mul_mod(r, r, modulus);
  u64 x3 = sub_mod(sub_mod(r2, j, modulus), mul_mod(2 % modulus, v, modulus), modulus);
  u64 y3 = sub_mod(
      mul_mod(r, sub_mod(v, x3, modulus), modulus),
      mul_mod(2 % modulus, mul_mod(s1, j, modulus), modulus), modulus);
  u64 z_sum = add_mod(left.z, right.z, modulus);
  u64 z3 = mul_mod(
      sub_mod(sub_mod(mul_mod(z_sum, z_sum, modulus), z1z1, modulus), z2z2, modulus),
      h, modulus);
  return {x3, y3, z3};
}

static Jacobian scalar_mul(u64 scalar, Jacobian point, u64 modulus) {
  Jacobian out = O;
  while (scalar) {
    if (scalar & 1) out = point_add(out, point, modulus);
    point = point_double(point, modulus);
    scalar >>= 1;
  }
  return out;
}

static u64 formal_parameter(const Jacobian &point, u64 modulus) {
  if (point.z == 0) return 0;
  return sub_mod(
      0,
      mul_mod(mul_mod(point.x, point.z, modulus), inv_mod(point.y, modulus), modulus),
      modulus);
}

static Jacobian curve_lift(u64 x0, u64 y0, u64 p, u64 x_shift) {
  u64 modulus = p * p;
  u64 x = (x0 + p * x_shift) % modulus;
  u64 rhs = add_mod(mul_mod(mul_mod(x, x, modulus), x, modulus), 7 % modulus, modulus);
  u64 y0_squared = mul_mod(y0, y0, modulus);
  u64 difference = sub_mod(rhs, y0_squared, modulus);
  if (difference % p) throw std::runtime_error("curve-lift defect not divisible by p");
  u64 delta = (difference / p) % p;
  u64 y_shift = mul_mod(delta, inv_mod((2 * y0) % p, p), p);
  u64 y = (y0 + p * y_shift) % modulus;
  if (sub_mod(
          mul_mod(y, y, modulus),
          add_mod(mul_mod(mul_mod(x, x, modulus), x, modulus), 7 % modulus, modulus),
          modulus) != 0) {
    throw std::runtime_error("curve lift failed");
  }
  return {x, y, 1};
}

static Jacobian torsion_lift_generator(u64 p, u64 order, u64 gx, u64 gy) {
  u64 modulus = p * p;
  u64 values[2];
  for (u64 shift = 0; shift < 2; ++shift) {
    Jacobian trial = curve_lift(gx, gy, p, shift);
    u64 parameter = formal_parameter(scalar_mul(order, trial, modulus), modulus);
    if (parameter % p) throw std::runtime_error("order image not in formal kernel");
    values[shift] = (parameter / p) % p;
  }
  u64 slope = sub_mod(values[1], values[0], p);
  u64 shift = mul_mod(sub_mod(0, values[0], p), inv_mod(slope, p), p);
  Jacobian lifted = curve_lift(gx, gy, p, shift);
  if (formal_parameter(scalar_mul(order, lifted, modulus), modulus) != 0) {
    throw std::runtime_error("torsion correction failed");
  }
  return lifted;
}

static void process_chunk(
    const std::vector<Jacobian> &points,
    u64 p,
    std::vector<std::uint32_t> &digits,
    u64 start_index) {
  u64 modulus = p * p;
  const std::size_t count = points.size();
  std::vector<u64> prefix(count + 1), inverse_z(count);
  prefix[0] = 1;
  for (std::size_t index = 0; index < count; ++index) {
    if (points[index].z % p == 0) throw std::runtime_error("nonunit projective z");
    prefix[index + 1] = mul_mod(prefix[index], points[index].z, modulus);
  }
  u64 accumulator = inv_mod(prefix[count], modulus);
  for (std::size_t index = count; index-- > 0;) {
    inverse_z[index] = mul_mod(accumulator, prefix[index], modulus);
    accumulator = mul_mod(accumulator, points[index].z, modulus);
  }
  for (std::size_t index = 0; index < count; ++index) {
    u64 inverse_z_squared = mul_mod(inverse_z[index], inverse_z[index], modulus);
    u64 x = mul_mod(points[index].x, inverse_z_squared, modulus);
    u64 residue = x % p;
    if (residue == 0) throw std::runtime_error("x=0 in frozen prime subgroup");
    u64 teichmueller = pow_mod(residue, p, modulus);
    u64 ratio = mul_mod(x, inv_mod(teichmueller, modulus), modulus);
    u64 delta = sub_mod(ratio, 1, modulus);
    if (delta % p) throw std::runtime_error("Teichmueller ratio not 1 modulo p");
    digits[start_index + index] = static_cast<std::uint32_t>((delta / p) % p);
  }
}

int main(int argc, char **argv) {
  if (argc != 7) {
    std::cerr << "usage: enumerator p n gx gy output.bin metadata.json\n";
    return 2;
  }
  u64 p = std::stoull(argv[1]);
  u64 order = std::stoull(argv[2]);
  u64 gx = std::stoull(argv[3]);
  u64 gy = std::stoull(argv[4]);
  std::string output_path = argv[5];
  std::string metadata_path = argv[6];
  if ((u128)p * p > (u128)UINT64_MAX) throw std::runtime_error("p^2 overflow");
  u64 modulus = p * p;
  if (sub_mod(
          mul_mod(gy, gy, p),
          add_mod(mul_mod(mul_mod(gx, gx, p), gx, p), 7 % p, p), p) != 0) {
    throw std::runtime_error("generator is off curve");
  }

  Jacobian generator = torsion_lift_generator(p, order, gx, gy);
  if (scalar_mul(order, generator, modulus).z != 0) {
    throw std::runtime_error("lifted generator order failed");
  }

  std::vector<std::uint32_t> digits(order, 0);
  const std::size_t chunk_size = 1u << 15;
  std::vector<Jacobian> chunk;
  chunk.reserve(chunk_size);
  Jacobian current = O;
  u64 chunk_start = 1;
  for (u64 scalar = 1; scalar < order; ++scalar) {
    current = point_add(current, generator, modulus);
    chunk.push_back(current);
    if (chunk.size() == chunk_size || scalar == order - 1) {
      process_chunk(chunk, p, digits, chunk_start);
      chunk_start += chunk.size();
      chunk.clear();
    }
  }
  if (point_add(current, generator, modulus).z != 0) {
    throw std::runtime_error("enumeration did not close");
  }

  std::ofstream output(output_path, std::ios::binary);
  output.write(
      reinterpret_cast<const char *>(digits.data()),
      static_cast<std::streamsize>(digits.size() * sizeof(std::uint32_t)));
  std::ofstream metadata(metadata_path);
  metadata << "{\n"
           << "  \"p\": " << p << ",\n"
           << "  \"n\": " << order << ",\n"
           << "  \"generator\": [" << gx << ", " << gy << "],\n"
           << "  \"count\": " << digits.size() << ",\n"
           << "  \"format\": \"little-endian uint32 indexed by scalar k\"\n"
           << "}\n";
  std::cerr << "enumerated n=" << order << "\n";
  return 0;
}
