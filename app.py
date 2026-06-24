from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from back_end.All3Feature.plotGraph import (
    PlotGraph,
    build_robustness_compare_series,
    plot_robustness_compare,
)
from back_end.All3Feature.utils import display_samples_by_label
import subprocess
import sys
import queue
import threading
import os
import json
from datetime import datetime
import argparse

app = Flask(__name__)

output_queues = {}
running_processes = {}

os.makedirs('logs', exist_ok=True)
os.makedirs('logs/recorded_logs', exist_ok=True)
RECORD_LOGS = False

# HELPER FUNCTIONS 
def read_stream(stream, session_id):
    for line in iter(stream.readline, ''):
        if line.strip():
            output_queues[session_id].put(line)

def run_process(script_args, session_id):
    # Completely disable shell, use list parameters to completely avoid command injection
    process = subprocess.Popen(
        script_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        universal_newlines=True,
        shell=False  # Absolutely disabled
    )
    running_processes[session_id] = process

    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, session_id))
    stdout_thread.daemon = True
    stdout_thread.start()

    process.wait()

    if session_id in running_processes:
        del running_processes[session_id]

    if session_id in output_queues:
        output_queues[session_id].put("__COMPLETE__")

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

# Client
@app.route('/start-client/basic_mode/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_basic_mode(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "3",
        "--server-address", server_address, "--label", label_string
    ])

@app.route('/start-client/availability_mode/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_availability_mode(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "3",
        "--server-address", server_address,
        "--use-random-disconnection", "--use-history-updates",
        "--disconnect-prob", "0.2", "--label", label_string
    ])

@app.route('/start-client/he_mode/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_he_mode(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "3",
        "--server-address", server_address, "--use-he", "--label", label_string
    ])

@app.route('/start-client/random_disconnect/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_random_disconnect(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "3",
        "--server-address", server_address,
        "--use-random-disconnection", "--disconnect-prob", "0.2",
        "--label", label_string
    ])

@app.route('/start-client/robustness_attack_nodefense/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_robustness_attack_nodefense(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "8",
        "--server-address", server_address, "--enable-poisoning"
    ])

@app.route('/start-client/robustness_attack_with_defense/<server_address>/<int:CID>/<label_string>', methods=['POST'])
def start_client_robustness_attack_with_defense(server_address, CID, label_string):
    return start_client([
        sys.executable, "-m", "back_end.All3Feature.client",
        "--cid", str(CID), "--num-clients", "8",
        "--server-address", server_address,
        "--enable-poisoning", "--use-defense"
    ])

# Server
@app.route('/start-server/basic_mode/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_basic_mode(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round)
    ])

@app.route('/start-server/availability_mode/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_availability_mode(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round),
        "--use-random-disconnection", "--use-history-updates",
        "--disconnect-prob", "0.2", "--max-stale-rounds", "5"
    ])

@app.route('/start-server/he_mode/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_he_mode(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round),
        "--use-he"
    ])

@app.route('/start-server/random_disconnect/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_random_disconnect(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round),
        "--use-random-disconnection", "--disconnect-prob", "0.2"
    ])

@app.route('/start-server/robustness_attack_nodefense/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_robustness_attack_nodefense(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round),
        "--enable-poisoning"
    ])

@app.route('/start-server/robustness_attack_with_defense/<int:num_round>/<int:num_client>', methods=['POST'])
def start_server_robustness_attack_with_defense(num_round, num_client):
    return start_server([
        sys.executable, "-m", "back_end.All3Feature.server",
        "--num-clients", str(num_client), "--num-rounds", str(num_round),
        "--enable-poisoning", "--use-defense"
    ])

def start_server(args_list):
    try:
        session_id = request.remote_addr
        output_queues[session_id] = queue.Queue()
        threading.Thread(target=run_process, args=(args_list, session_id), daemon=True).start()
        return jsonify(success=True, message="Server started")
    except Exception as e:
        return jsonify(success=False, message=str(e))

def start_client(args_list):
    try:
        session_id = request.remote_addr
        output_queues[session_id] = queue.Queue()
        threading.Thread(target=run_process, args=(args_list, session_id), daemon=True).start()
        return jsonify(success=True, message="Client started")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/stop-training', methods=['POST'])
def stop_training():
    session_id = request.remote_addr
    if session_id in running_processes:
        running_processes[session_id].kill()
        del running_processes[session_id]
        if session_id in output_queues:
            output_queues[session_id].put("Training stopped")
            output_queues[session_id].put("__COMPLETE__")
        return jsonify(success=True, message="Stopped")
    return jsonify(success=False, message="No process")

@app.route('/start-simulate/<filename>', methods=['POST'])
def start_simulate(filename):
    try:
        session_id = request.remote_addr
        output_queues[session_id] = queue.Queue()
        args = [sys.executable, "-u", "Simulator.py", "--file", f"{filename}.json", "--speed", "100"]
        threading.Thread(target=run_process, args=(args, session_id), daemon=True).start()
        return jsonify(success=True, message="Simulation started")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/stream')
def stream():
    session_id = request.remote_addr
    def generate():
        sid = session_id
        if sid not in output_queues:
            if output_queues:
                sid = next(iter(output_queues.keys()))
            else:
                yield "data: No active session\n\n"
                return
        q = output_queues[sid]
        json_log = None
        if RECORD_LOGS:
            os.makedirs("logs/recorded_logs", exist_ok=True)
            json_log = open(f'logs/recorded_logs/stream_{datetime.now():%Y%m%d_%H%M%S}.json', 'a', encoding='utf-8')

        yield ": connected\n\n"
        while True:
            try:
                out = q.get(timeout=10)
                s = str(out).rstrip()
                if json_log:
                    json_log.write(json.dumps({"ts": str(datetime.now()), "line": s}, ensure_ascii=False) + "\n")
                if s == "__COMPLETE__":
                    yield f"data: {s}\n\n"
                    break
                yield f"data: {s}\n\n"
            except queue.Empty:
                yield ": heartbeat\n\n"
        if json_log:
            json_log.close()
        if sid in output_queues:
            del output_queues[sid]
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
    })

@app.route('/images_mnist/<path:filename>')
def serve_images(filename):
    return send_from_directory('images_mnist', filename)

@app.route('/generate-plot/<int:max_rounds>', methods=['POST'])
def plot_graph(max_rounds):
    data = request.get_json()
    history = data.get('history')
    os.makedirs('static', exist_ok=True)
    plotter = PlotGraph(max_rounds=max_rounds)
    plotter.plot(history, plot_path='static/training_plot.png')
    return send_from_directory('static', 'training_plot.png')

@app.route('/api/robustness-compare-data', methods=['GET'])
def api_robustness_compare_data():
    log_dir = os.path.join('logs', 'simulator_logs')
    series, max_round_cap = build_robustness_compare_series(log_dir)
    if not series:
        return jsonify(success=False, message="No log data"), 400
    max_steps = max(len(s['rounds']) for s in series)
    return jsonify(success=True, series=series, max_round_cap=max_round_cap, max_steps=max_steps, interval_ms=350)

@app.route('/generate-robustness-compare-plot', methods=['GET'])
def robustness_compare_plot():
    log_dir = os.path.join('logs', 'simulator_logs')
    series, max_r = build_robustness_compare_series(log_dir)
    if not series:
        return jsonify(success=False, message="No data"), 400
    histories = [{'rounds': s['rounds'], 'global_acc': s['global_acc']} for s in series]
    labels = [s['label'] for s in series]
    os.makedirs('static', exist_ok=True)
    plot_robustness_compare(histories, labels, max_r, plot_path='static/robustness_compare.png')
    return send_from_directory('static', 'robustness_compare.png')

@app.route('/display-label')
def display_label():
    os.makedirs('static/image_folder/label_samples', exist_ok=True)
    display_samples_by_label()
    return jsonify(success=True, message="Label images generated")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=5000)
    args = parser.parse_args()
    app.run(debug=True, port=args.port, threaded=True)