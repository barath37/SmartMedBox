import java.util.*;

// --- 1. Producer Consumer ---
class SharedBuffer {
    int item;
    boolean hasItem = false;

    synchronized void produce(int value) {
        try {
            if (hasItem) {
                wait();
            }
            item = value;
            System.out.println("Produced item: " + item);
            hasItem = true;
            notify();
        } catch (Exception e) {
            System.out.println(e);
        }
    }

    synchronized void consume() {
        try {
            if (!hasItem) {
                wait();
            }
            System.out.println("Consumed item: " + item);
            hasItem = false;
            notify();
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}

class Producer extends Thread {
    SharedBuffer buffer;
    Producer(SharedBuffer b) {
        buffer = b;
    }
    public void run() {
        for (int i = 1; i <= 3; i++) {
            buffer.produce(i);
        }
    }
}

class Consumer extends Thread {
    SharedBuffer buffer;
    Consumer(SharedBuffer b) {
        buffer = b;
    }
    public void run() {
        for (int i = 1; i <= 3; i++) {
            buffer.consume();
        }
    }
}

// --- 2. File Downloader ---
class FileChunk implements Runnable {
    String chunkName;
    
    FileChunk(String name) {
        chunkName = name;
    }
    
    public void run() {
        System.out.println("Downloading " + chunkName + "...");
        try {
            Thread.sleep(1000); 
        } catch (Exception e) {
            System.out.println(e);
        }
        System.out.println(chunkName + " download complete.");
    }
}

// --- 3. Bank Account ATM ---
class BankAccount {
    int balance = 10000;

    // The word 'synchronized' fixes the race condition. 
    // If you delete it, both ATMs can withdraw 8000 at the same time and ruin the balance.
    synchronized void withdraw(int amt, String name) {
        System.out.println(name + " trying to withdraw " + amt);
        if (balance >= amt) {
            try {
                Thread.sleep(500); // Simulate processing time
            } catch (Exception e) {}
            
            balance -= amt;
            System.out.println(name + " success. New balance: " + balance);
        } else {
            System.out.println(name + " failed. Not enough balance.");
        }
    }
}

class ATM extends Thread {
    BankAccount acc;
    int amt;
    String name;
    
    ATM(BankAccount a, int amount, String n) {
        acc = a;
        amt = amount;
        name = n;
    }
    
    public void run() {
        acc.withdraw(amt, name);
    }
}

// --- Main Class ---
public class Java_Lab_6 {
    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        int choice = 0;

        do {
            System.out.println("\n--- Lab Exercise 6 ---");
            System.out.println("1. Producer Consumer");
            System.out.println("2. File Downloader");
            System.out.println("3. Bank Account");
            System.out.println("4. Exit");
            System.out.print("Enter choice: ");
            
            try {
                choice = scan.nextInt();
                switch (choice) {
                    case 1:
                        testProducerConsumer();
                        break;
                    case 2:
                        testDownloader();
                        break;
                    case 3:
                        testBank();
                        break;
                    case 4:
                        System.out.println("Exiting...");
                        break;
                    default:
                        System.out.println("Invalid choice.");
                }
            } catch (Exception e) {
                System.out.println("Invalid input.");
                scan.nextLine(); // clear buffer
            }
        } while (choice != 4);
        scan.close();
    }

    public static void testProducerConsumer() {
        SharedBuffer b = new SharedBuffer();
        Producer p = new Producer(b);
        Consumer c = new Consumer(b);
        
        p.start();
        c.start();
        
        try {
            p.join();
            c.join();
        } catch (Exception e) {}
    }

    public static void testDownloader() {
        Thread t1 = new Thread(new FileChunk("Part 1"));
        Thread t2 = new Thread(new FileChunk("Part 2"));
        Thread t3 = new Thread(new FileChunk("Part 3"));
        
        t1.start();
        t2.start();
        t3.start();
        
        try {
            t1.join();
            t2.join();
            t3.join();
            System.out.println("All parts combined successfully.");
        } catch (Exception e) {}
    }

    public static void testBank() {
        BankAccount acc = new BankAccount();
        
        ATM user1 = new ATM(acc, 8000, "User 1");
        ATM user2 = new ATM(acc, 8000, "User 2");
        
        user1.start();
        user2.start();
        
        try {
            user1.join();
            user2.join();
        } catch (Exception e) {}
    }
}