import "./styles.scss";
import TimeseriesChart from "./components/TimeseriesChart";

function App() {
  return (
    <div className="App">
      <meta
        httpEquiv="Content-Security-Policy"
        content="upgrade-insecure-requests"
      />
      <h2>OCR_Analytics</h2>
      <TimeseriesChart />
    </div>
  );
}

export default App;
