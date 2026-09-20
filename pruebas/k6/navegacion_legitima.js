import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
const etiqueta = __ENV.ESCENARIO || 'local';

export const options = {
  vus: Number(__ENV.VUS || 2),
  duration: __ENV.DURACION || '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1000'],
  },
  tags: { escenario: etiqueta },
};

export default function () {
  const respuestas = http.batch([
    ['GET', `${baseUrl}/`, null, { tags: { ruta: 'inicio' } }],
    ['GET', `${baseUrl}/buscar?q=teclado`, null, { tags: { ruta: 'buscar' } }],
  ]);
  for (const respuesta of respuestas) {
    check(respuesta, {
      'respuesta normal no es 5xx': (r) => r.status < 500,
    });
  }
  sleep(1);
}

export function handleSummary(data) {
  const salida = __ENV.SUMMARY_FILE || `resultado-${etiqueta}.json`;
  return { [salida]: JSON.stringify(data, null, 2) };
}
