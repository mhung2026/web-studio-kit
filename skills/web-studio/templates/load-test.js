// Mau k6 do web-tech-architect dien lai khi du an co backend va chuan bi qua cong G4.
// Nguong va base URL lay tu ADR da duyet (xem studio/ENGINEERING.md §4 "Load test").
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // TODO: ramp-up theo so nguoi dung muc tieu trong ADR
    { duration: '1m', target: 10 },  // TODO: steady state
    { duration: '30s', target: 0 },  // TODO: ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // TODO: nguong p95 theo ADR
    http_req_failed: ['rate<0.01'],   // TODO: ti le loi chap nhan duoc theo ADR
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/`); // TODO: thay bang endpoint that can kiem tai
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
