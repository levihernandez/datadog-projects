package com.faztpay.accounts;

// import com.faztpay.accounts.controller.PaymentController;
import com.faztpay.accounts.model.AccountModel;
import com.faztpay.accounts.repository.AccountRepository;
import org.junit.jupiter.api.BeforeEach;
// import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
// import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.UUID;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class AccountIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private AccountRepository accountRepository;

    // @Autowired
    // private PaymentController paymentController;

    private String uniqueUsername;
    private UUID accountUuId;


    @BeforeEach
    public void setUp() {
        // No need to set up MockMvc here; it's automatically configured by
        // @AutoConfigureMockMvc
        uniqueUsername = "user_" + System.currentTimeMillis(); // Generate a unique username
        accountUuId = UUID.randomUUID(); // Generate a new UUID
        // mockMvc = MockMvcBuilders.standaloneSetup(paymentController).build();
    }

    // @AfterEach
    // void tearDown() {
    //     accountRepository.deleteAll(); // Clear all accounts after each test
    // }


    // @Test
    // void createDemoUsername() throws Exception{
    //     AccountModel account = new AccountModel();
    //     account.setId(accountUuId);
    //     account.setBalance(BigDecimal.valueOf(0)); // Initial balance
    //     account.setUsername(uniqueUsername); // Set the unique username
    //     accountRepository.save(account);
    // }

    @Test
    void testSubmitPayment() throws Exception {

        AccountModel account = new AccountModel();

        account.setId(accountUuId);
        account.setBalance(BigDecimal.valueOf(100.0));
        account.setUsername(uniqueUsername); // Set the username
        account.setCreatedAt(Timestamp.valueOf(LocalDateTime.now())); // Set creation timestamp
        account.setUpdatedAt(Timestamp.valueOf(LocalDateTime.now())); // Set update timestamp

        try {
            accountRepository.save(account);
            // Log account details
            System.out.println("Account created: " + accountUuId.toString());
        } catch (DataIntegrityViolationException e) {
            // Handle duplicate key scenario
            System.out.println("Duplicate key exception: " + e.getMessage());
        }



        // Perform the request to submit payment with the username parameter
        mockMvc.perform(post("/api/payments/submit")
                .param("accountId", accountUuId.toString())  // Pass accountId as a request parameter
                .param("username", uniqueUsername)          // Pass username as a request parameter
                .param("amount", "50.0")                   // Pass amount as a request parameter
                .contentType(MediaType.APPLICATION_FORM_URLENCODED))
                .andExpect(status().isOk());

    }

    @Test
    void testWithdrawMoney() throws Exception {
        AccountModel account = new AccountModel();
        account.setId(accountUuId);
        account.setBalance(BigDecimal.valueOf(100.0));
        account.setUsername(uniqueUsername); // Set the username
        account.setCreatedAt(Timestamp.valueOf(LocalDateTime.now())); // Set creation timestamp
        account.setUpdatedAt(Timestamp.valueOf(LocalDateTime.now())); // Set update timestamp

        try {
            accountRepository.save(account);
            // Log account details
            System.out.println("Account created: " + accountUuId.toString());
        } catch (DataIntegrityViolationException e) {
            // Handle duplicate key scenario
            System.out.println("Duplicate key exception: " + e.getMessage());
        }

        

        // Perform the withdrawal request with the username parameter
        mockMvc.perform(post("/api/payments/withdraw")
                .param("accountId", accountUuId.toString())  // Pass accountId as a request parameter
                .param("username", uniqueUsername)          // Pass username as a request parameter
                .param("amount", "50.0")                   // Pass amount as a request parameter
                .contentType(MediaType.APPLICATION_FORM_URLENCODED))
                .andExpect(status().isOk());
    }
}
