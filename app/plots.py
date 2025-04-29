import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, subprocess

def generate_plots(log_type, csv_file_path, output_dir="plots"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Set delimiter based on log type
    delim = '!' if log_type == "android" else ','

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Split into rows and skip the header
    rows = [line.strip().split(delim) for line in lines if line.strip()]
    data = rows[1:]  # Skipping header

    num = 0

    if log_type == "apache":
        levels = []
        events = []
        times = []
        time_counts = {}
        event_count={}
        prev = None
        timestamps = []

        # Parse CSV for Apache log
        for row in data:
            num += 1
            if len(row) < 2:
                return "NO LOGS FOUND FOR GIVEN TIME RANGE"

            day = row[1]
            timestr = row[2]
            time = int(row[7].strip())
            level = row[3].lower()
            event = row[5].strip()

            timestamps.append(f"{day} {timestr[:-8]} {timestr[-4:]}")
            levels.append(level)
            events.append(event)
            times.append(time)

            if time == prev:
                time_counts[time] += 1
            else:
                time_counts[time] = 1

            prev = time

        # ---- EVENTS PER TIME (LINE PLOT) ----
        # print("Time counts:", time_counts)
        tick_indices = [0,int(num/5),int(2*num/5),int(3*num/5),int(4*num/5),num-1]  # print only 6 timestamps for better readability, the graph is qualitative anyway

        # get corresponding timestamps and time positions
        x_ticks = [timestamps[i] for i in tick_indices]
        x_positions = [times[i] for i in tick_indices]

        # Prepare all seconds for the plot
        all_seconds = np.arange(min(time_counts.keys()), max(time_counts.keys()) + 1)     # we need the timestamps not present in the logfile as well for the plot

        for stamp in all_seconds:
            if stamp not in time_counts:
                time_counts[stamp] = 0                                                      # events/sec for such time stamps is 0

        y = [time_counts[sec] for sec in all_seconds]
        x = all_seconds

        plt.figure(figsize=(12, 6))
        plt.plot(x, y, marker='.', linestyle='-', markersize=3, linewidth=1.2)
        plt.xlabel("Time")
        plt.ylabel("Events/sec")

        # Adjust x-ticks to match selected timestamps
        plt.xticks(ticks=x_positions, labels=x_ticks, rotation=90)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "plot1.png"))
        plt.close()
        
        
        
        # ---- PLOT 2: Level State Distribution (Pie Chart) ----
        unique_levels, counts = np.unique(levels, return_counts=True)

        plt.figure(figsize=(6, 6))
        plt.pie(
            counts,
            labels=unique_levels,
            autopct="%1.1f%%",
            startangle=90,
            colors=["#66c2a5", "#fc8d62", "#e78ac3", "#a6d854"][:len(unique_levels)],
        )
        plt.title("Apache: Level State Distribution")
        plt.axis("equal")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot2.png"))
        plt.close()


        # ---- PLOT 3: Event Code Distribution (Bar Chart) ----
        valid_event_codes = ["E1", "E2", "E3", "E4", "E5", "E6", "-"]  # define all valid codes

        unique_codes, code_counts = np.unique(events, return_counts=True)

        # fill in missing codes with 0 count
        code_dict = dict(zip(unique_codes, code_counts))
        full_counts = [code_dict.get(code, 0) for code in valid_event_codes]

        plt.figure(figsize=(8, 5))
        plt.bar(valid_event_codes, full_counts, color="#8da0cb")
        plt.title("Apache: Event Code Distribution")
        plt.xlabel("Event Code")
        plt.ylabel("Count")
        plt.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot3.png"))
        plt.close()
        

        subprocess.run(['rm', csv_file_path])

    elif log_type == "syslog":

        # Line Plot: Event Count Over Time
        times = []
        components = []
        time_counts = {}
        prev = None
        timestamps = []

        # Parse CSV
        for row in data:
            num += 1
            if len(row) < 2:
                return "NO LOGS FOUND FOR GIVEN TIME RANGE"

            timestr = row[1]
            time = int(row[6].strip())
            component = row[3]
            
            components.append(component)

            timestamps.append(f"{timestr}")
            times.append(time)

            if time == prev:
                time_counts[time] += 1
            else:
                time_counts[time] = 1

            prev = time

        # ---- EVENTS PER TIME (LINE PLOT) ----
        # print("Time counts:", time_counts)
        tick_indices = [0,int(num/5),int(2*num/5),int(3*num/5),int(4*num/5),num-1]  # print only 6 timestamps for better readability, the graph is qualitative anyway

        # get corresponding timestamps and time positions
        x_ticks = [timestamps[i] for i in tick_indices]
        x_positions = [times[i] for i in tick_indices]

        # Prepare all seconds for the plot
        all_seconds = np.arange(min(time_counts.keys()), max(time_counts.keys()) + 1)     # we need the timestamps not present in the logfile as well for the plot

        for stamp in all_seconds:
            if stamp not in time_counts:
                time_counts[stamp] = 0                                                      # events/sec for such time stamps is 0

        y = [time_counts[sec] for sec in all_seconds]
        x = all_seconds

        plt.figure(figsize=(12, 6))
        plt.plot(x, y, marker='.', linestyle='-', markersize=3, linewidth=1.2)
        plt.xlabel("Time")
        plt.ylabel("Events/sec")
        plt.xticks(ticks=x_positions, labels=x_ticks, rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot1.png"))
        plt.title("Syslog: Event Count Over Time")
        plt.close()

        # Bar Chart: Top Log Sources (Component)
        unique, counts = np.unique(components, return_counts=True)
        sorted_indices = np.argsort(-counts)[:5]  # top 5
        plt.figure()
        plt.bar(unique[sorted_indices], counts[sorted_indices])
        plt.title("Syslog: Top Log Sources")
        plt.xlabel("Component")
        plt.ylabel("Count")
        plt.savefig(f"{output_dir}/plot3.png")
        plt.close()
        
        subprocess.run(['rm', csv_file_path])

    elif log_type == "android":
        # Parse CSV for Android log

        

        # Line Plot: Traffic Trends (events/sec vs time)
        times = []
        time_counts = {}
        components = []
        levels =[]
        prev = None
        timestamps = []
        num=0

        # Parse CSV for Android log
        for row in data:
            num+=1
            if len(row) < 2:                                        
                return "NO LOGS FOUND FOR GIVEN TIME RANGE"

            timestr = row[1][:-4]                                       #actual timestamp (hence timestr - time string)
            time = int(row[7].strip())                               #time as seconds since epoch

            timestamps.append(f"{timestr[:-3]}")         # formatted strings for the plot
            times.append(time)
            component = row[5]
            level = row[4]
            
            components.append(component)
            levels.append(level)

            if time == prev:
                time_counts[time] += 1
            else:
                time_counts[time] = 1
                

            prev = time
            
            
        tick_indices = [0,int(num/2),num-1]

        # get corresponding timestamps and time positions
        x_ticks = [timestamps[i] for i in tick_indices]
        x_positions = [times[i] for i in tick_indices]

        # Prepare all seconds for the plot
        all_seconds = np.arange(min(time_counts.keys()), max(time_counts.keys()) + 1)     # we need the timestamps not present in the logfile as well for the plot

        for stamp in all_seconds:
            if stamp not in time_counts:
                time_counts[stamp] = 0                                                      # events/sec for such time stamps is 0

        y = [time_counts[sec] for sec in all_seconds]
        x = all_seconds

        plt.figure(figsize=(12, 9))
        plt.plot(x, y, marker='.', linestyle='-', markersize=3, linewidth=1.2)
        plt.xlabel("Time")
        plt.ylabel("Events/sec")
        plt.title("Android: Traffic Trends Over Time")
        plt.xticks(ticks=x_positions, labels=x_ticks, rotation=90)
        plt.savefig(f"{output_dir}/plot2.png")
        plt.close()
        
        # Bar Chart: Top Log Sources
        unique, counts = np.unique(components, return_counts=True)
        sorted_indices = np.argsort(-counts)[:5]  # top 5
        plt.figure(figsize=(12, 6))
        plt.bar(unique[sorted_indices], counts[sorted_indices])
        plt.title("Android: Event Component Distribution")
        plt.xlabel("Component")
        plt.ylabel("Count")
        plt.savefig(f"{output_dir}/plot1.png")
        plt.close()

        # Pie Chart: Level Breakdown
        unique, counts = np.unique(levels, return_counts=True)
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=unique, autopct='%1.1f%%')
        plt.title("Android: Level Breakdown")
        plt.savefig(f"{output_dir}/plot3.png")
        plt.close()
        
        subprocess.run(['rm', csv_file_path])
        
    else :
        print("wrong log format")
        
