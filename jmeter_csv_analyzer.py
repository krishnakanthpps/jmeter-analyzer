#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt


class JMeterAnalyzer:
  def __init__(self):
    self.result_file=""
    self.response_times = {}
    self.results = {}
    self.sample_count = {}
    self.error_count ={}
    self.RESPONSE_TIME_INDEX = 1
    self.SAMPLE_NAME_INDEX = 2
    self.SAMPLE_STATUS_INDEX = 4


  def run(self, opts, args):
    for opt, arg in opts:
      if opt in ('-f'):
        self.result_file = arg
    with open (self.result_file) as rf:
      for line in rf:
        self.parse(line)
    self.calculate()
    with open (self.result_file + "_analyzed.csv", "w") as af:
      af.write("Sample Name, Count, Average, 90%, Min, Max, Median, Errors\n")
      for res in self.results:
        agh =  str(self.results[res])
        agh = agh.lstrip('[')
        agh = agh.replace(']', '\n')
        af.write(agh)

  def calculate(self):
    for sample in self.response_times:
      rts = map(int, self.response_times[sample])
      self.results[sample] = [sample, self.sample_count[sample], self.average(rts),self.percentile(rts, 90),
                                        min(rts), max(rts), self.median(rts), self.error_count[sample]]

  def median(self, array):
    array.sort()
    return array[len(array)/2]

  def average(self, array):
    return float("%.4f" % round(sum(array)/float(len(array)), 4))

  def percentile(self, array, percent):
    array.sort()
    return array[int(round(len(array)*percent/100))]

  def parse(self, line):
    components = line.split(',')
    sample_name = components[self.SAMPLE_NAME_INDEX]
    if sample_name in self.response_times:
      self.response_times[sample_name].append(components[self.RESPONSE_TIME_INDEX])
      self.sample_count[sample_name] = self.sample_count[sample_name] +1
      if components[self.SAMPLE_STATUS_INDEX] == "ERROR": self.error_count[sample_name] += 1
    else:
      self.response_times[sample_name] = [components[self.RESPONSE_TIME_INDEX]]
      self.sample_count[sample_name] = 1
      self.error_count[sample_name] = 0 if components[self.SAMPLE_STATUS_INDEX] == "OK" else 1

def print_usage():
    print '''Usage: JMEterAnalylzer.py -f <jmeter-resultfile>
Analyzes a csv-formatted JMeter sample results log file and generates an csv file summarizing performance results
NOTE: you need to output te JMeter sample result log in csv format
Use the property jmeter.save.saveservice.output_format=csv'''

def main(argv):
        try: opts, args = getopt.getopt(argv, 'f:', ["file="])
        except getopt.GetoptError as error:
            print error
            print_usage()
            sys.exit(2)
        if len(opts) < 1:
            print_usage()
            sys.exit(2)
        analyzer = JMeterAnalyzer()
        try:
            analyzer.run(opts, args)
        except ValueError as verror:
            print >> sys.stderr, "Received a ValueError: " + str(verror)
            sys.exit(1)
        except AssertionError as aserror:
            print >> sys.stderr, str(aserror)
            sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

