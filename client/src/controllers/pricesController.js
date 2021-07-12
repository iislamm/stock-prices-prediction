import moment from "moment";

const url = "https://stock-prediction-backend.click";

const formatDate = (date) => moment(date).format("MMMM D YYYY");

export const get_prices = async (symbol) => {
  const res = await fetch(`${url}/prices/${symbol}`);
  const body = await res.json();
  let { prices } = body;

  prices = prices.map((p) => ({
    ...p,
    close: p.close ? Number(Number(p.close).toFixed(2)) : 0,
    prediction: Number(Number(p.prediction).toFixed(2)),
    change: Number((Number(p.change) * 100).toFixed(2)),
    date: formatDate(p.date),
  }));

  prices.sort((a, b) => new Date(a.date) - new Date(b.date));

  // for (let p in prices) {
  //   tradingDays.push(prices[p].date);
  // }

  // predictions = predictions.map((p) => ({
  //   prediction: Number(Number(p.close).toFixed(2)),
  //   date: formatDate(p.date),
  // }));

  // console.log({ predictions });

  // console.log({ tradingDays });

  // predictions = predictions.filter(
  //   (p) =>
  //     new Date(p.date) > Math.max.apply(null, tradingDays.map(t => new Date(t))) ||
  //     tradingDays.includes(p.date)
  // );

  // predictions.sort((a, b) => new Date(a.date) - new Date(b.date));

  // console.log(predictions.length);

  const { stock } = body;

  return { prices, stock };
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
