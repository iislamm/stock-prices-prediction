import moment from "moment";

const url = "https://stock-prediction-backend.click";

const formatDate = (date) => moment(date).format("MMMM D YYYY");

export const get_prices = async (symbol) => {
  const res = await fetch(`${url}/prices/${symbol}`);
  const body = await res.json();
  let { prices, predictions } = body;
  let tradingDays = []

  prices = prices.map((p) => ({
    ...p,
    close: Number(Number(p.close).toFixed(2)),
    change: Number((Number(p.change) * 100).toFixed(2)),
    date: formatDate(p.date),
  }));

  prices.sort((a, b) => new Date(a.date) - new Date(b.date));

  for (let p in prices) {
    tradingDays.push(new Date(prices[p].date))
  }

  predictions = predictions.map((p) => ({
    prediction: Number(Number(p.close).toFixed(2)),
    date: formatDate(p.date),
  }));

  predictions = predictions.filter(
    (p) =>
      new Date(p.date) > Math.max.apply(null, tradingDays) ||
      tradingDays.includes(new Date(p.date))
  );

  predictions.sort((a, b) => new Date(a.date) - new Date(b.date));

  const { stock } = body;

  return { prices, stock, predictions };
};

export const get_predictions = async (symbol) => {
  const res = await fetch(`${url}/predict/${symbol}`);
  const body = await res.json();

  let predictions = body.predictions;
  predictions = predictions.map((p) => ({
    prediction: p.close,
    date: formatDate(p.date),
  }));
  delete predictions.close;
  console.log({ predictions });
  return predictions;
};
