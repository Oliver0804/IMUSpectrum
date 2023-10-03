from flask import Flask, request, send_from_directory
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PLOT_FOLDER = 'plots'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    df = pd.read_csv(filepath)
    time = df['時間標記']
    fig, ax = plt.subplots()
    ax.plot(time, df['ax'], label='ax')
    ax.plot(time, df['ay'], label='ay')
    ax.plot(time, df['az'], label='az')
    ax.plot(time, df['gx'], label='gx')
    ax.plot(time, df['gy'], label='gy')
    ax.plot(time, df['gz'], label='gz')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    plot_path_time = os.path.join(PLOT_FOLDER, f"time_{file.filename.split('.')[0]}.png")
    plt.savefig(plot_path_time)
    plt.close(fig)

    freqs, psd = welch(df['ax']) # 使用ax軸的資料進行頻譜分析，也可以使用其他軸
    fig, ax = plt.subplots()
    ax.semilogy(freqs, psd)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power/Frequency (dB/Hz)')
    plot_path_freq = os.path.join(PLOT_FOLDER, f"freq_{file.filename.split('.')[0]}.png")
    plt.savefig(plot_path_freq)
    plt.close(fig)

    return render_template('results.html', time_plot=plot_path_time, frequency_plot=plot_path_freq)


@app.route('/plots/<filename>', methods=['GET'])
def serve_plot(filename):
    return send_from_directory(PLOT_FOLDER, filename)


from flask import render_template

@app.route('/')
def index():
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8080)
