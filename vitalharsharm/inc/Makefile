CC = g++

CFLAGS = -g -O2 -Wall -std=c++0x
EXECUTABLE = test
TEST_SOURCES = $(wildcard *.cpp)

.SUFFIXES: .cpp .o

.cpp.o:
	$(CC) $(CFLAGS) -c -o $@ $<

$(EXECUTABLE): $(TEST_SOURCES)
	$(CC) $(CFLAGS) -o $@ $^

all: $(EXECUTABLE)

mem: CFLAGS += -DSHOW_MEM
mem: $(EXECUTABLE)

noid: CFLAGS += -DMAKE_PARANOID
noid: $(EXECUTABLE)

memnoid: CFLAGS += -DSHOW_MEM -DMAKE_PARANOID
memnoid: $(EXECUTABLE)

clean:
	$(RM) $(EXECUTABLE)
	$(RM) *.o
