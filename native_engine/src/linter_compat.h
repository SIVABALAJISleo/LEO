#ifndef LINTER_COMPAT_H
#define LINTER_COMPAT_H

/**
 * LINTER COMPATIBILITY LAYER
 * 
 * This header provides a minimal set of declarations to satisfy linters (like clangd)
 * when system headers are not available or misconfigured in the environment.
 * It is only intended for static analysis and should not interfere with real builds.
 */

#if defined(__clang__) || defined(__GNUC__)

#include <stddef.h>

// Basic Types
#ifndef __uint128_t
typedef unsigned __int128 __uint128_t;
#endif

typedef unsigned long long uint64_t;
typedef unsigned int uint32_t;
typedef unsigned short uint16_t;
typedef unsigned char uint8_t;
typedef long long int64_t;
typedef int int32_t;
typedef short int16_t;
typedef signed char int8_t;

// Forward declarations
namespace std {
    template<typename T> class initializer_list {
    public:
        const T* _begin;
        size_t _size;
        const T* begin() const { return _begin; }
        const T* end() const { return _begin + _size; }
        size_t size() const { return _size; }
    };

    class ostream {
    public:
        ostream& operator<<(const char*);
        ostream& operator<<(int);
        ostream& operator<<(unsigned int);
        ostream& operator<<(long long);
        ostream& operator<<(unsigned long long);
        ostream& operator<<(double);
        ostream& operator<<(void*);
    };
    extern ostream cout;
    static const char* endl = "\n";
}

// Minimal std namespace
namespace std {
    typedef ::size_t size_t;
    
    template<typename T1, typename T2> struct pair {
        T1 first;
        T2 second;
    };

    template<typename T> class vector {
    public:
        vector() {}
        vector(size_t n) {}
        vector(size_t n, const T& val) {}
        vector(std::initializer_list<T> list) {}
        void push_back(const T&);
        void resize(size_t);
        size_t size() const;
        bool empty() const;
        T& operator[](size_t);
        const T& operator[](size_t) const;
        T* begin();
        T* end();
        const T* begin() const;
        const T* end() const;
        T* data();
    };

    class string {
    public:
        string() {}
        string(const char*) {}
        string(const string&) {}
        bool empty() const;
        const char* c_str() const;
        size_t length() const;
        size_t size() const;
        char& operator[](size_t);
        const char& operator[](size_t) const;
        string operator+(const string&) const;
        string operator+(const char*) const;
        string& operator+=(const char*);
        string& operator+=(char);
        string& operator+=(int);
        bool operator<(const string&) const;
        bool operator==(const string&) const;
        char* begin();
        char* end();
        const char* begin() const;
        const char* end() const;
    };

    template<typename K, typename V> class map {
    public:
        V& operator[](const K&);
        struct iterator {
            std::pair<K, V>* operator->();
            bool operator!=(const iterator&) const;
            bool operator==(const iterator&) const;
            iterator& operator++();
        };
        iterator find(const K&);
        iterator begin();
        iterator end();
    };

    template<typename T> class set {
    public:
        void insert(const T&);
        struct iterator {
            const T* operator->();
            bool operator!=(const iterator&) const;
            bool operator==(const iterator&) const;
            iterator& operator++();
        };
        iterator find(const T&);
        iterator begin();
        iterator end();
    };

    // pair moved up

    namespace chrono {
        struct nanoseconds { long long count() const; };
        struct microseconds { long long count() const; };
        struct milliseconds { long long count() const; };
        template<typename T, typename U> T duration_cast(U);
        struct time_point {
            long long operator-(const time_point&) const;
        };
        struct high_resolution_clock {
            static time_point now();
        };
    }

    template<typename T, typename... Args> void sort(T, T, Args...);
    
    // Memory allocation
    void* aligned_alloc(size_t, size_t);
    void free(void*);
    
    class stringstream {
    public:
        stringstream() {}
        stringstream(const string&) {}
        stringstream& operator<<(const string&);
        stringstream& operator<<(uint64_t);
        stringstream& operator>>(string&);
        string str() const;
        operator bool() const { return true; }
    };
}

// C functions
extern "C" {
    int printf(const char*, ...);
    int sprintf(char*, const char*, ...);
    int snprintf(char*, size_t, const char*, ...);
    void* memset(void*, int, size_t);
    void* memcpy(void*, const void*, size_t);
    char* strdup(const char*);
    char* strtok(char*, const char*);
    int strcmp(const char*, const char*);
    void free(void*);
    void* malloc(size_t);
    int tolower(int);
}

#define NULL 0

#endif // __clang__ || __GNUC__

#endif // LINTER_COMPAT_H
