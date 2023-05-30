import React, { useState, useEffect } from "react";
import "chart.js/auto";
import dayjs from "dayjs";
import zoomPlugin from "chartjs-plugin-zoom";
import "chartjs-adapter-moment";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import axios from "axios";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
  Button,
} from "@mui/material";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers-pro";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  zoomPlugin,
  Title,
  Tooltip,
  Legend
);

const DEFAULT_BUSINESS = "walgreens";

const getOptions = (category) => {
  let label;
  if (category == "amount") {
    label = "Analytics for total amount";
  } else if (category == "avgScore") {
    label = "Analytics for average score";
  } else if (category == "medianScore") {
    label = "Analytics for median score";
  } else if (category == "medianOcrScore") {
    label = "Analytics for median OCR score";
  } else {
    label = "Analytics for average OCR score";
  }
  return {
    responsive: true,
    scales: {
      x: {
        type: "time",
        time: {
          unit: "minute",
          displayFormats: {
            minute: "HH:mm",
          },
        },
        ticks: { source: "auto" },
        offset: false,
        grid: {
          drawBorder: true,
          drawOnChartArea: false,
          drawTicks: true,
        },
        font: {
          size: 8,
        },
      },
      xAxis3: {
        type: "time",
        time: {
          unit: "day",
        },
      },
    },
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: label,
        font: {
          size: 18,
        },
      },
      zoom: {
        pan: {
          enabled: true,
          mode: "x",
        },
        zoom: {
          wheel: {
            enabled: true,
          },
          enabled: true,
          drag: true,
          mode: "xy",
        },
      },
    },
  };
};

const TimeseriesChart = () => {
  let now = new Date();
  now.setDate(now.getDate() + 1);
  const defaultStart = new Date(new Date().setDate(now.getDate() - 1));

  const [amountChartData, setAmountChartData] = useState({});
  const [avgScoreChartData, setAvgScoreChartData] = useState({});
  const [avgOcrScoreChartData, setAvgOcrScoreChartData] = useState({});
  const [medianScoreChartData, setMedianScoreChartData] = useState({});
  const [medianOcrScoreChartData, setMedianOcrScoreChartData] = useState({});
  const [chartType, setChartType] = useState("hour");
  const [businessIdOptions, setBusinessIdOptions] = useState([]);
  const [businessId, setBusinessId] = useState(DEFAULT_BUSINESS);
  const [startDate, setStartDate] = useState(defaultStart);
  const [endDate, setEndDate] = useState(now);

  useEffect(() => {
    fetchChartData(chartType);
  }, []);

  useEffect(() => {
    fetchBusinessIds();
  }, []);

  const fetchBusinessIds = async () => {
    try {
      const response = await axios.get(
        "http://138.197.208.92:5000/api/business_ids"
      );
      const result = response.data;
      setBusinessIdOptions(result);
    } catch {}
  };

  const getAverage = (arr) => {
    return (
      Math.round(
        (arr.reduce((partialSum, a) => partialSum + parseFloat(a), 0) /
          arr.length) *
          100
      ) / 100
    );
  };

  const fetchChartData = async (chartType) => {
    try {
      const data = {
        start_time: new Date(startDate.setUTCHours(0, 0, 0, 0)),
        end_time: new Date(endDate.setUTCHours(0, 0, 0, 0)),
        business_id: businessId,
      };
      const response = await axios.post(
        "http://138.197.208.92:5000/api/" + chartType + "data",
        data
      );
      const result = response.data;
      const labelMap = {};

      // aggregating the values for records with the same timestamp
      result.forEach(function (record) {
        let tsString = record.ts;
        if (!(tsString in labelMap)) {
          labelMap[tsString] = {
            totalAmounts: [],
            avgScores: [],
            medianScores: [],
            avgOcrScores: [],
            medianOcrScores: [],
          };
        }
        labelMap[tsString].totalAmounts.push(record.total_amount);
        labelMap[tsString].avgScores.push(record.avg_score);
        labelMap[tsString].medianScores.push(record.median_score);
        labelMap[tsString].avgOcrScores.push(record.avg_ocr_score);
        labelMap[tsString].medianOcrScores.push(record.median_ocr_score);
      });
      let labels = [],
        amounts = [],
        avgScores = [],
        medianScores = [],
        avgOcrScores = [],
        medianOcrScores = [];

      const sortedLabels = Object.keys(labelMap).sort(function (a, b) {
        return new Date(a) - new Date(b);
      });

      sortedLabels.forEach(function (key) {
        labels.push(key);
        let amount = labelMap[key].totalAmounts.reduce(
          (partialSum, a) => partialSum + a,
          0
        );
        amounts.push(amount);
        let avgScore = getAverage(labelMap[key].avgScores);
        avgScores.push(avgScore);

        let medianScore = getAverage(labelMap[key].medianScores);
        medianScores.push(medianScore);

        let avgOcrScore = getAverage(labelMap[key].avgOcrScores);
        avgOcrScores.push(avgOcrScore);

        let medianOcrScore = getAverage(labelMap[key].medianOcrScores);
        medianOcrScores.push(medianOcrScore);
      });

      setAmountChartData({
        labels,
        datasets: [
          {
            label: "Total amount($)",
            data: amounts,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      });
      setAvgScoreChartData({
        labels,
        datasets: [
          {
            label: "Average score",
            data: avgScores,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      });

      setAvgOcrScoreChartData({
        labels,
        datasets: [
          {
            label: "Average ocr score",
            data: avgOcrScores,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      });

      setMedianScoreChartData({
        labels,
        datasets: [
          {
            label: "Median score",
            data: medianScores,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      });

      setMedianOcrScoreChartData({
        labels,
        datasets: [
          {
            label: "Median ocr score",
            data: medianOcrScores,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      });
    } catch (error) {
      console.error("Error fetching timeseries data:", error);
    }
  };

  if (
    !Object.keys(amountChartData).length ||
    !Object.keys(avgScoreChartData).length ||
    !Object.keys(avgOcrScoreChartData).length ||
    !Object.keys(medianScoreChartData).length ||
    !Object.keys(medianOcrScoreChartData).length
  ) {
    return (
      <div>
        <h3>Loading Data</h3>
      </div>
    );
  }

  const handleFilter = () => {
    fetchChartData(chartType);
  };

  return (
    <div className="container">
      <meta
        http-equiv="Content-Security-Policy"
        content="upgrade-insecure-requests"
      >
        <div className="filter-panel">
          <FormControl
            fullWidth
            className="form"
            sx={{
              display: "flex",
              flexDirection: "row",
              gap: "10px",
            }}
            onSubmit={(event) => event.preventDefault()}
          >
            <InputLabel>Business</InputLabel>
            <Select
              sx={{ minWidth: 120 }}
              value={businessId}
              onChange={(event) => setBusinessId(event.target.value)}
              autoWidth
              label="Business"
            >
              {businessIdOptions.length ? (
                businessIdOptions.map((option) => (
                  <MenuItem value={option}>{option}</MenuItem>
                ))
              ) : (
                <MenuItem value={null}>None</MenuItem>
              )}
            </Select>
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="de">
              <DatePicker
                label="Start Date"
                value={dayjs(startDate)}
                onChange={(newValue) => setStartDate(newValue.$d)}
              />
              <DatePicker
                label="End Date"
                value={dayjs(endDate)}
                onChange={(newValue) => setEndDate(newValue.$d)}
              />
            </LocalizationProvider>
            <ToggleButtonGroup
              color="primary"
              value={chartType}
              exclusive
              onChange={(event) => setChartType(event.target.value)}
              aria-label="Platform"
            >
              <ToggleButton value="minute">Minute</ToggleButton>
              <ToggleButton value="hour">Hour</ToggleButton>
            </ToggleButtonGroup>
            <Button variant="outlined" onClick={handleFilter} size="medium">
              Generate
            </Button>
          </FormControl>
        </div>
        <div className="chart-container">
          <Line
            className="chart"
            options={getOptions("amount")}
            data={amountChartData}
          />
          <Line
            className="chart"
            options={getOptions("avgScore")}
            data={avgScoreChartData}
          />
          <Line
            className="chart"
            options={getOptions("medianScore")}
            data={medianScoreChartData}
          />
          <Line
            className="chart"
            options={getOptions("avgOcrScore")}
            data={avgOcrScoreChartData}
          />
          <Line
            className="chart"
            options={getOptions("medianOcrScore")}
            data={medianOcrScoreChartData}
          />
        </div>
      </meta>
    </div>
  );
};

export default TimeseriesChart;
