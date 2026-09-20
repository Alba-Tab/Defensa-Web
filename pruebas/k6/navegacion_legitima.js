import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
const etiqueta = __ENV.ESCENARIO || 'local';
const respuestas429 = new Rate('respuestas_429');

export const options = {
  vus: Number(__ENV.VUS || 2),
  duration: __ENV.DURACION || '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1000'],
    respuestas_429: ['rate==0'],
  },
  tags: { escenario: etiqueta },
};

export default function () {
  const respuestas = http.batch([
    ['GET', `${baseUrl}/`, null, { tags: { ruta: 'inicio' } }],
    ['GET', `${baseUrl}/buscar?q=teclado`, null, { tags: { ruta: 'buscar' } }],
  ]);
  for (const respuesta of respuestas) {
    respuestas429.add(respuesta.status === 429);
    check(respuesta, {
      'respuesta normal no es 5xx': (r) => r.status < 500,
      'navegación legítima no se limita': (r) => r.status !== 429,
    });
  }
  sleep(1);
}

export function handleSummary(data) {
  const salida = __ENV.SUMMARY_FILE || `resultado-${etiqueta}.json`;
  return { [salida]: JSON.stringify(data, null, 2) };
}
