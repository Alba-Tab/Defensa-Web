import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1').replace(/\/$/, '');
const ruta = __ENV.RUTA || '/';
const metodo = (__ENV.METODO || 'GET').toUpperCase();
const respuestas429 = new Rate('respuestas_429');
const erroresServidor = new Rate('errores_servidor');

export const options = {
  scenarios: {
    rafaga: {
      executor: 'constant-arrival-rate',
      rate: Number(__ENV.TASA || 30),
      timeUnit: '1s',
      duration: __ENV.DURACION || '10s',
      preAllocatedVUs: 10,
      maxVUs: 50,
    },
  },
  thresholds: {
    respuestas_429: ['rate>0'],
    errores_servidor: ['rate==0'],
  },
};

export default function () {
  const url = `${baseUrl}${ruta}`;
  const respuesta = metodo === 'POST'
    ? http.post(url, JSON.stringify({ email: 'prueba@lab.local', password: 'incorrecta' }), {
        headers: { 'Content-Type': 'application/json' },
      })
    : http.get(url);

  respuestas429.add(respuesta.status === 429);
  erroresServidor.add(respuesta.status >= 500);
  check(respuesta, {
    'nginx responde o limita': (r) => r.status < 500,
  });
}
