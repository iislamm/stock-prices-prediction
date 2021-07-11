import React from "react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { get_prices } from "../controllers/pricesController";
import ArrowUpword from "@material-ui/icons/ArrowUpward";
import ArrowDownward from "@material-ui/icons/ArrowDownward";

function getWindowDimensions() {
  const { innerWidth: width, innerHeight: height } = window;
  return {
    width,
    height,
  };
}

function CompanyPage() {
  const [prices, setPrices] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [data, setData] = useState(null);
  const [stock, setStock] = useState(null);
  const { symbol } = useParams();
  const [windowDimensions, setWindowDimensions] = useState(
    getWindowDimensions()
  );
  const [chartWidth, setChartWidth] = useState(900);
  const [priceRange, setPriceRange] = useState(null);

  useEffect(() => {
    if (!prices) {
      get_prices(symbol).then(({ prices, stock, predictions }) => {
        setPrices(prices);
        setStock(stock);
        setPredictions(predictions);
        setData([...prices.slice(-20, -1), ...predictions]);
      });
    }
    console.log({ data });
  }, [data, prices, predictions, symbol]);

  useEffect(() => {
    setPrices(null);
    setData(null);
  }, [symbol]);

  useEffect(() => {
    function handleResize() {
      getWindowDimensions();
      setWindowDimensions(getWindowDimensions());
    }

    if (windowDimensions.width < 960 && windowDimensions.width > 700) {
      setChartWidth(700);
    } else if (windowDimensions.width < 700) {
      setChartWidth(windowDimensions.width - 50);
    }

    window.addEventListener("resize", handleResize, true);
    return () => window.removeEventListener("resize", handleResize);
  }, [windowDimensions]);

  useEffect(() => {
    const getPriceRange = () => {
      if (data) {
        let sorted_prices = data;
        sorted_prices = sorted_prices.map((p) =>
          p.prediction ? { ...p, close: p.prediction } : p
        );
        sorted_prices.sort((a, b) => Number(a.close) - Number(b.close));

        const min = sorted_prices[0].close;
        const max = sorted_prices[sorted_prices.length - 1].close;

        console.log({ min, max });
        return [Number(min), Number(max)];
      }
    };
    setPriceRange(getPriceRange());
  }, [data]);

  return (
    <div>
      {stock && data ? (
        <React.Fragment>
          <header>
            <h1>
              {stock && stock.company_name} -{" "}
              <span>{stock && stock.symbol}</span>
            </h1>
            <h4
              className={
                prices[prices.length - 1].change > 0
                  ? "positive-change"
                  : "negative-change"
              }
            >
              {prices[prices.length - 1].change > 0 ? (
                <ArrowUpword />
              ) : (
                <ArrowDownward />
              )}
              {prices[prices.length - 1].change}%
            </h4>
          </header>
          <LineChart
            className="chart"
            width={chartWidth}
            height={400}
            data={data}
          >
            <Line type="monotone" dataKey="close" stroke="#8884d8" />
            {predictions && (
              <Line type="monotone" dataKey="prediction" stroke="#bd84d8" />
            )}
            <XAxis dataKey="date" />
            <YAxis type="number" domain={priceRange} />
            <Tooltip />
          </LineChart>
        </React.Fragment>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default CompanyPage;
