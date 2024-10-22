#include "Daemon.hpp"

#include <iostream>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>

#include "AbyssServer.hpp"
#include "Data.hpp"

using namespace std;

bool Daemon::quit = false;
int Daemon::exit_value = 0;

// called at exit
void Daemon::shutdown() {
  cerr << "Daemon::shutdown" << endl;
}

// Handle various signals
void Daemon::handler(int signum) {

  if(signum == SIGINT) {
    cerr << "Daemon::handler caught CTRL-C" << endl;
    Daemon::quit = true;
  } else {
    cerr << "Daemon::handler caught signal: " << signum << endl;
  }
}

int main(int argc, char *argv[]) {

  // call handler() at CTRL-C (signum = SIGINT)
  if(signal(SIGINT, SIG_IGN) != SIG_IGN) {
    signal(SIGINT, Daemon::handler);
  }

  // call shutdown() at program exit
  atexit(Daemon::shutdown);

  // Example data container for domain logic
  Data data;

  // To communicate between URScript and the executable we use the xmlrpc-c library
  // This library is standard available on the robot and in the development toolchain.
  AbyssServer gui(&data);

  pthread_t thread_id;
  if(pthread_create(&thread_id, NULL, gui.run, &gui)){
    cerr << "Couldn't create pthread" << endl;
    return EXIT_FAILURE;
  }

  cout << "Daemon started" << endl;

  pthread_join(thread_id, NULL);

  cout << "Daemon stopped" << endl;

  return Daemon::exit_value;
}
