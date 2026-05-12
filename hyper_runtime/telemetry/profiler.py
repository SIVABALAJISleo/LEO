import cProfile
import pstats
import io

class PerformanceProfiler:
    def __init__(self):
        self.pr = cProfile.Profile()
        
    def start(self):
        self.pr.enable()
        
    def stop(self):
        self.pr.disable()
        
    def print_stats(self, sort_by='cumulative', lines=20):
        s = io.StringIO()
        ps = pstats.Stats(self.pr, stream=s).sort_stats(sort_by)
        ps.print_stats(lines)
        print(s.getvalue())
