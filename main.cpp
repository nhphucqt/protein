#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include <map>
#include <cassert>

struct Point3D {
    double x, y, z;

    Point3D(double x, double y, double z) : x(x), y(y), z(z) {}
    Point3D() : x(0), y(0), z(0) {}

    Point3D operator+(const Point3D& other) const {
        return Point3D(x + other.x, y + other.y, z + other.z);
    }

    Point3D operator-(const Point3D& other) const {
        return Point3D(x - other.x, y - other.y, z - other.z);
    }

    Point3D operator*(double scalar) const {
        return Point3D(x * scalar, y * scalar, z * scalar);
    }

    double operator*(const Point3D& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    Point3D operator%(const Point3D& other) const {
        // cross product
        return Point3D(y * other.z - z * other.y, z * other.x - x * other.z, x * other.y - y * other.x);
    }

    double length() const {
        return sqrt(x * x + y * y + z * z);
    }

    void normalize() {
        double len = length();
        x /= len;
        y /= len;
        z /= len;
    }
};

struct Face {
    Point3D a, b, c;

    Face() {}
    Face(Point3D a, Point3D b, Point3D c) : a(a), b(b), c(c) {}

    Point3D normal() const {
        return (b - a) % (c - a);
    }

    void reverseOrder() {
        std::swap(a, c);
    }

    Point3D intersect(const Point3D& a, const Point3D& v) const {
        Point3D n = normal();
        double t = (n * (this->a - a)) / (n * v);
        return a + (v * t);
    }

    bool isContain(const Point3D& p) const {
        Point3D n = normal();
        Point3D v1 = b - a;
        Point3D v2 = c - a;
        Point3D v = p - a;
        double dot1 = v * (v1 % v2);
        double dot2 = n * (v1 % v);
        double dot3 = n * (v % v2);
        return dot1 >= 0 && dot2 >= 0 && dot3 >= 0;
    }

    double angle(const Face& f) const {
        Point3D n1 = normal();
        Point3D n2 = f.normal();
        return acos((n1 * n2) / (n1.length() * n2.length()));
    }
};

struct Mesh {
    std::vector<Point3D> vertices;
    std::vector<Face> faces;
    std::vector<std::vector<int>> adjList;
    std::vector<std::array<int, 3>> faceVex;

    std::vector<std::array<int, 2>> edges;

    void input(std::ifstream& fin) {
        int numVertices, numFaces;
        fin >> numVertices >> numFaces;
        vertices.resize(numVertices);
        faces.resize(numFaces);
        faceVex.resize(numFaces);
        for (int i = 0; i < numVertices; ++i) {
            int r, g, b;
            fin >> vertices[i].x >> vertices[i].y >> vertices[i].z >> r >> b >> b;
        }

        std::map<std::pair<int, int>, std::vector<int>> edgeToFace;

        for (int i = 0; i < numFaces; ++i) {
            int n;
            int a, b, c;
            int r, g, bb;
            fin >> n >> a >> b >> c >> r >> g >> bb;
            faces[i] = Face(vertices[a], vertices[b], vertices[c]);
            faceVex[i] = {a, b, c};
            edgeToFace[{std::min(a, b), std::max(a, b)}].push_back(i);
            edgeToFace[{std::min(b, c), std::max(b, c)}].push_back(i);
            edgeToFace[{std::min(c, a), std::max(c, a)}].push_back(i);
        }

        adjList.resize(numFaces);
        for (auto &it : edgeToFace) {
            assert(it.second.size() == 2);
            adjList[it.second[0]].push_back(it.second[1]);
            adjList[it.second[1]].push_back(it.second[0]);
        }
    }

    void output(std::ofstream& fout) {
        for (int i = 0; i < (int)faces.size(); ++i) {
            Point3D centr = (faces[i].a + faces[i].b + faces[i].c) * (1.0 / 3);
            Point3D norm = faces[i].normal();
            norm.normalize();
            Point3D outer = centr + norm;
            fout << outer.x << " " << outer.y << " " << outer.z << " " << 255 << " " << 0 << " " << 0 << std::endl;
        }
    }

    void outputEdge(std::ofstream& fout) {
        int cur = 66220; 
        for (int i = 0; i < (int)faces.size(); ++i) {
            fout << faceVex[i][0] << ' ' << cur << ' ' << 255 << ' ' << 0 << ' ' << 0 << '\n';
            // fout << faceVex[i][1] << ' ' << cur << ' ' << 255 << ' ' << 0 << ' ' << 0 << '\n';
            // fout << faceVex[i][2] << ' ' << cur << ' ' << 255 << ' ' << 0 << ' ' << 0 << '\n';
            cur++;
        }
    }

    bool isOuterFace(const int idx) const {
        int cnt = 0;
        Point3D centr = (faces[idx].a + faces[idx].b + faces[idx].c) * (1.0 / 3);
        Point3D norm = (faces[idx].b - faces[idx].a) % (faces[idx].c - faces[idx].a);
        for (int i = 0; i < (int)faces.size(); ++i) {
            if (i == idx) continue;
            cnt += faces[i].isContain(faces[i].intersect(centr, norm));
        }
        return !(cnt & 1);
    }

    void fixOrientation() {
        for (int i = 0; i < (int)faces.size(); ++i) {
            if (!isOuterFace(i)) {
                faces[i].reverseOrder();
            }
        }
    }

    std::pair<std::array<int, 2>, Point3D> matchVec(int a, int b) {
        std::vector<int> v;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                if (faceVex[a][i] == faceVex[b][j]) {
                    v.push_back(i);
                }
            }
        }
        if (v[0] == 0 && v[1] == 2) {
            std::swap(v[0], v[1]);
        }
        v[0] = faceVex[a][v[0]];
        v[1] = faceVex[a][v[1]];
        std::array<int, 2> res = {v[0], v[1]};
        return std::make_pair(res, vertices[v[1]] - vertices[v[0]]);
    }

    void process() {
        for (int i = 0; i < (int)faces.size(); ++i) {
            for (int x : adjList[i]) {
                if (i > x) continue;
                std::array<int, 2> li;
                Point3D va;
                tie(li, va) = matchVec(i, x);
                Point3D vb = faces[i].normal() % faces[x].normal();
                // edges.push_back(li);
                if (va * vb < 0) {
                    double angle = acos(-1) - fabs(faces[i].angle(faces[x]));
                    std::cerr << angle / acos(-1) * 180 << std::endl;
                    if (angle <= acos(-1) * 0.90) {
                        edges.push_back(li);
                    }
                    // fout << li[0] << ' ' << li[1] << ' ' << 255 << ' ' << 0 << ' ' << 0 << '\n';
                }
            }
        }
        // int cur = vertices.size();
        // for (int i = 0; i < (int)faces.size(); ++i) {
        //     Point3D centr = (faces[i].a + faces[i].b + faces[i].c) * (1.0 / 3);
        //     Point3D norm = faces[i].normal();
        //     norm.normalize();
        //     Point3D outer = centr + norm;
        //     vertices.push_back(outer);
        //     edges.push_back({faceVex[i][0], cur});
        //     edges.push_back({faceVex[i][1], cur});
        //     edges.push_back({faceVex[i][2], cur});
        //     cur++;
        // }
    }

    void print(std::ofstream& fout) {
        fout << "ply";
        fout << '\n' << "format ascii 1.0";
        fout << '\n' << "comment ball mesh";
        fout << '\n' << "element vertex " << vertices.size();
        fout << '\n' << "property float x";
        fout << '\n' << "property float y";
        fout << '\n' << "property float z";
        fout << '\n' << "property uchar red";
        fout << '\n' << "property uchar green";
        fout << '\n' << "property uchar blue";

        // fout << '\n' << "element face " << faces.size();
        // fout << '\n' << "property list uchar int vertex_indices";
        // fout << '\n' << "property uchar red";
        // fout << '\n' << "property uchar green";
        // fout << '\n' << "property uchar blue";

        fout << '\n' << "element edge " << edges.size();
        fout << '\n' << "property int32 vertex1";
        fout << '\n' << "property int32 vertex2";
        fout << '\n' << "property uint8 red";
        fout << '\n' << "property uint8 green";
        fout << '\n' << "property uint8 blue";
        fout << '\n' << "end_header";
        fout << '\n';
        for (int i = 0; i < (int)vertices.size(); ++i) {
            fout << vertices[i].x << ' ' << vertices[i].y << ' ' << vertices[i].z << ' ' << 0 << ' ' << 0 << ' ' << 0 << '\n';
        }
        // for (int i = 0; i < (int)faces.size(); ++i) {
        //     fout << 3 << ' ' << faceVex[i][0] << ' ' << faceVex[i][1] << ' ' << faceVex[i][2] << ' ' << 0 << ' ' << 255 << ' ' << 0 << '\n';
        // }
        for (int i = 0; i < (int)edges.size(); ++i) {
            fout << edges[i][0] << ' ' << edges[i][1] << ' ' << 255 << ' ' << 0 << ' ' << 0 << '\n';
        }
    }
};


int main() {
    std::ifstream fin("input.txt");
    // std::ifstream fin("tetrahedron.txt");
    fin.tie(nullptr)->sync_with_stdio(false);
    std::ofstream fout("output.txt");
    Mesh mesh;
    mesh.input(fin);
    // mesh.fixOrientation();
    // mesh.output(fout);

    // std::ofstream foutEdge("outputEdge.txt");
    // mesh.outputEdge(foutEdge);

    // std::ofstream foutEdge("outputEdge.txt");
    mesh.process();
    fout.close();
    fout.open("demo4.ply");
    mesh.print(fout);

    return 0;
}