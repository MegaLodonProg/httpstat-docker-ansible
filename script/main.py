from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable
import requests

LOGGER = logging.getLogger("httpstat")

@dataclass(frozen=True)
class RequestSpec:
	label: str
	url: str


class HttpStatusError(RuntimeError):
	def __init__(self, status_code: int, url: str, body: str) -> None:
		message = f"{url} returned error status {status_code}"
		super().__init__(message)
		self.status_code = status_code
		self.url = url
		self.body = body


REQUESTS: tuple[RequestSpec, ...] = (
	RequestSpec("informational", "https://httpstat.us/102"),
	RequestSpec("success", "https://httpstat.us/200"),
	RequestSpec("redirect", "https://httpstat.us/302"),
	RequestSpec("client_error", "https://httpstat.us/404"),
	RequestSpec("server_error", "https://httpstat.us/500"),
)


def configure_logging() -> None:
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s %(levelname)s %(name)s - %(message)s",
	)


def fetch(url: str) -> requests.Response:
	response = requests.get(url, timeout=10, allow_redirects=False)
	response.encoding = response.encoding or "utf-8"
	return response


def handle_response(label: str, response: requests.Response) -> None:
	status_code = response.status_code
	body = response.text.strip()

	if 100 <= status_code < 400:
		LOGGER.info(
			"%s: status=%s body=%r",
			label,
			status_code,
			body,
		)
		return

	if 400 <= status_code < 600:
		raise HttpStatusError(status_code, response.url, body)

	LOGGER.warning("%s: unexpected status=%s body=%r", label, status_code, body)


def run_requests(requests_to_run: Iterable[RequestSpec]) -> int:
	failures = 0

	for request_spec in requests_to_run:
		LOGGER.info("Starting request %s -> %s", request_spec.label, request_spec.url)

		try:
			response = fetch(request_spec.url)
			handle_response(request_spec.label, response)
		except HttpStatusError as exc:
			failures += 1
			LOGGER.error(
				"%s: exception raised for %s: %s (body=%r)",
				request_spec.label,
				exc.url,
				exc,
				exc.body,
			)
		except requests.RequestException as exc:
			failures += 1
			LOGGER.exception("%s: transport error: %s", request_spec.label, exc)

	return failures


def main() -> int:
	configure_logging()
	failures = run_requests(REQUESTS)

	if failures == 0:
		LOGGER.info("Completed all requests successfully")
	else:
		LOGGER.warning("Completed with %s request error(s)", failures)

	return 0 if failures == 0 else 1


if __name__ == "__main__":
	raise SystemExit(main())
