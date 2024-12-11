
                from locust import HttpUser, task, between

                class CustomQueryUser(HttpUser):
                    wait_time = between(1, 5)
                    host = "http://localhost"  # Dummy host

                    @task
                    def test_p_static_part(self):
                        pass
                