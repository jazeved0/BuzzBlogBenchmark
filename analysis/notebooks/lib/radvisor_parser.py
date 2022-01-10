# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

"""
Simple dataclass-based parsers for both rAdvisor target (container) logs
and buffer flush logs
"""

from dataclasses import dataclass
from typing import List, Dict, Iterable, Any, Tuple, Union, OrderedDict
from yaml import Loader
import csv

# Minimum target log version that this supports
MIN_TARGET_LOG_VERSION="1.3.0"


@dataclass
class IOStatsCgroupV1:
    read: int
    write: int
    sync: int
    asyn: int


@dataclass
class TargetLogEntryCgroupV1:
    read: int
    # PID stats
    pids_current: int
    pids_max: Union[int, str]
    # CPU stats
    cpu_usage_total: int
    cpu_usage_system: int
    cpu_usage_user: int
    cpu_usage_percpu: List[int]
    cpu_stat_user: int
    cpu_stat_system: int
    cpu_throttling_periods: int
    cpu_throttling_throttled_count: int
    cpu_throttling_throttled_time: int
    # Memory stats
    memory_usage_current: int
    memory_usage_max: int
    memory_limit_hard: int
    memory_limit_soft: int
    memory_failcnt: int
    memory_hierarchical_limit_memory: int
    memory_hierarchical_limit_memoryswap: int
    memory_cache: int
    memory_rss_all: int
    memory_rss_huge: int
    memory_mapped: int
    memory_swap: int
    memory_paged_in: int
    memory_paged_out: int
    memory_fault_total: int
    memory_fault_major: int
    memory_anon_inactive: int
    memory_anon_active: int
    memory_file_inactive: int
    memory_file_active: int
    memory_unevictable: int
    # Block IO stats
    blkio_time: int
    blkio_sectors: int
    blkio_service_bytes: IOStatsCgroupV1
    blkio_service_ios: IOStatsCgroupV1
    blkio_service_time: IOStatsCgroupV1
    blkio_queued: IOStatsCgroupV1
    blkio_wait: IOStatsCgroupV1
    blkio_merged: IOStatsCgroupV1
    blkio_throttle_service_bytes: IOStatsCgroupV1
    blkio_throttle_service_ios: IOStatsCgroupV1
    blkio_bfq_service_bytes: IOStatsCgroupV1
    blkio_bfq_service_ios: IOStatsCgroupV1

    @staticmethod
    def make(row: Dict[str, str]) -> 'TargetLogEntryCgroupV1':
        def i(key: str) -> int:
            """Attempts to parse a cell to an int, or returns 0"""
            if key in row and row[key] is not None and len(row[key]) > 0:
                return int(row[key])
            return 0

        def io(key_prefix: str) -> IOStatsCgroupV1:
            """Makes an IOStats instance from the key prefix"""
            return IOStatsCgroupV1(
                read=i(f"{key_prefix}.read"),
                write=i(f"{key_prefix}.write"),
                sync=i(f"{key_prefix}.sync"),
                asyn=i(f"{key_prefix}.async"))

        # Every field is an int, except for pids_max, cpu_usage_percpu,
        # and blkio.* (with the exception of blkio.time and blkio.sectors),
        # and every field is the same as its column label,
        # except s/./_/

        io_keys = {k for k in row if (
            k.startswith("blkio.") and k not in {"blkio.time", "blkio.sectors"})}
        io_fields = {k.replace('.', '_'): io(v) for k, v in row if k in io_keys}

        int_keys = {k for k in row if (
            k not in {"pids.max", "cpu.usage.percpu"} and k not in io_keys)}
        int_fields = {k.replace('.', '_'): i(v) for k, v in row if k in int_keys}

        pids_max = "max" if row["pids.max"] == "max" else i("pids.max")
        cpu_usage_percpu = []
        if len(row["cpu.usage.percpu"]) > 0:
            cpu_usage_percpu = [i(s) for s in row["cpu.usage.percpu"].split(" ")]

        return TargetLogEntryCgroupV1(**io_fields, **int_fields, pids_max=pids_max, cpu_usage_percpu=cpu_usage_percpu)


@dataclass
class TargetLogEntryCgroupV2:
    read: int
    # PID stats
    pids_current: int
    pids_max: Union[int, str]
    # CPU stats
    cpu_stat__usage_usec: int
    cpu_stat__system_usec: int
    cpu_stat__user_usec: int
    cpu_stat__nr_periods: int
    cpu_stat__nr_throttled: int
    cpu_stat__throttled_usec: int
    # Memory stats
    memory_current: int
    memory_high: int
    memory_max: int
    memory_stat__anon: int
    memory_stat__file: int
    memory_stat__kernel_stack: int
    memory_stat__pagetables: int
    memory_stat__percpu: int
    memory_stat__sock: int
    memory_stat__shmem: int
    memory_stat__file_mapped: int
    memory_stat__file_dirty: int
    memory_stat__file_writeback: int
    memory_stat__swapcached: int
    memory_stat__inactive_anon: int
    memory_stat__active_anon: int
    memory_stat__inactive_file: int
    memory_stat__active_file: int
    memory_stat__unevictable: int
    memory_stat__pgfault: int
    memory_stat__pgmajfault: int
    # Block IO stats
    io_stat__rbytes: int
    io_stat__wbytes: int
    io_stat__rios: int
    io_stat__wios: int
    io_stat__dbytes: int
    io_stat__dios: int

    @staticmethod
    def make(row: Dict[str, str]) -> 'TargetLogEntryCgroupV2':
        def i(key: str) -> int:
            """Attempts to parse a cell to an int, or returns 0"""
            if key in row and row[key] is not None and len(row[key]) > 0:
                return int(row[key])
            return 0

        # Every field is an int, except for pids_max,
        # and every field is the same as its column label,
        # except s/./_/ and s/\//__/
        fields = {k.replace('.', '_').replace('/', '__'): i(v) for k, v in row if k != "pids.max"}
        pids_max = "max" if row["pids.max"] == "max" else i("pids.max")
        return TargetLogEntryCgroupV2(**fields, pids_max=pids_max)

@dataclass
class BufferFlushLogEntry:
    timestamp: int
    target_id: str
    written: int
    success: bool

    @staticmethod
    def make(row: Dict[str, str]) -> 'BufferFlushLogEntry':
        return BufferFlushLogEntry(
            timestamp=int(row["timestamp"]),
            target_id=row["target_id"],
            written=int(row["written"]),
            success=row["success"].lower() == 'true')


def parse_target_log(lines: Iterable[str]) -> Tuple[Union[Iterable[TargetLogEntryCgroupV1], Iterable[TargetLogEntryCgroupV2]], Dict[str, Any]]:
    """
    Loads an output target file from rAdvisor into
    a lazy iterator of either TargetLogEntryCgroupV1's or TargetLogEntryCgroupV2's
    in the order of logging, in addition to the metadata dictionary
    contained at the top of the logfile.
    """

    metadata = {}
    yaml_lines = []

    # Skip the first yaml delimeter
    next(lines)

    # Load all lines until the end of the yaml section
    while True:
        try:
            line = next(lines)
        except StopIteration:
            break
        else:
            if line.startswith("---"):
                break
            yaml_lines.append(line)

    # Load YAML to dictionary
    yaml_str = "\n".join(yaml_lines)
    yaml_loader = Loader(yaml_str)
    metadata = yaml_loader.get_data()

    # Check the version string
    version = metadata.get("Version", "0.0.0")
    if version < MIN_TARGET_LOG_VERSION:
        print(f"Warning: rAdvisor log version '{version}' "
            f"is less than minimum version '{MIN_TARGET_LOG_VERSION}'")

    # Check the collector type
    collector_type = metadata.get("CollectorType", "cgroup_v1")
    
    csv_reader = csv.DictReader(lines)
    def generator():
        for row in csv_reader:
            try:
                if collector_type == "cgroup_v1":
                    yield TargetLogEntryCgroupV1.make(row)
                elif collector_type == "cgroup_v2":
                    yield TargetLogEntryCgroupV2.make(row)
            except Exception as e:
                print(e)
                print("An error ocurred. continuing...\n")

    return (generator(), metadata)


def parse_buffer_flush_log(lines: Iterable[str]) -> OrderedDict[int, BufferFlushLogEntry]:
    """
    Loads a buffer flush log from rAdvisor into an ordered dictionary
    of timestamp (int) -> BufferFlushLogEntry in the order of logging.
    """

    entries = OrderedDict()
    csv_reader = csv.DictReader(lines)
    try:
        for row in csv_reader:
            log_entry = BufferFlushLogEntry.make(row)
            entries[log_entry.timestamp] = log_entry
    except Exception as e:
        print(e)
        print("An error ocurred. continuing...\n")

    return entries
